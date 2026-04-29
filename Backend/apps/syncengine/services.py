import hashlib

from django.db import connection, transaction
from django.utils import timezone
from apps.syncengine.models import SyncCursor
from apps.boards.models import Board
from apps.failures.models import FailureCase
from apps.intelligence.models import RepairHistory
from apps.repairs.services import (
    cancel_tickets_for_invalidated_failure,
    close_tickets_for_repaired_failure,
    has_confirmed_repair_workflow,
    get_or_create_open_ticket_for_failure,
)
from apps.testresults.models import TestResult


KO_RESULTS = {
    TestResult.Result.FAILED,
    TestResult.Result.ERROR,
    TestResult.Result.TERMINATED,
}

ENRICHED_VIEW_NAME = "public.v3_test_events_enriched"


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def normalize_result(value: str) -> str:
    v = (value or "").strip().upper()
    mapping = {
        "PASS": TestResult.Result.PASSED,
        "PASSED": TestResult.Result.PASSED,
        "FAIL": TestResult.Result.FAILED,
        "FAILED": TestResult.Result.FAILED,
        "ERROR": TestResult.Result.ERROR,
        "TERMINATED": TestResult.Result.TERMINATED,
        "": TestResult.Result.ERROR,
    }
    return mapping.get(v, TestResult.Result.ERROR)


def normalize_phase(value: str) -> str:
    v = (value or "").strip().lower()

    if "final" in v:
        return TestResult.Phase.FINAL_TEST
    if "etanch" in v or "étanch" in v or "leak" in v:
        return TestResult.Phase.LEAK_TEST
    if "dever" in v or "burn" in v or "aging" in v:
        return TestResult.Phase.BURN_IN_TEST
    if "norm" in v:
        return TestResult.Phase.NORMATIVE_TEST
    return TestResult.Phase.BOARD_TEST


def build_source_event_key(row: dict) -> str:
    raw = "|".join(
        [
            str(row.get("sn_global") or ""),
            str(row.get("reference_client") or ""),
            str(row.get("reference_interne") or ""),
            str(row.get("station_id") or ""),
            str(row.get("phase") or ""),
            str(row.get("result_norm") or ""),
            str(row.get("event_ts") or ""),
            str(row.get("defect_exact_norm") or row.get("defect_message") or ""),
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def fetch_enriched_rows(last_ingested_ts=None, limit: int = 500):
    sql = f"""
        SELECT
            sn_global,
            reference_client,
            reference_interne,
            operator_name,
            station_id,
            defect_type,
            defect_type_norm,
            defect_message,
            defect_exact_norm,
            event_ts,
            ingested_ts,
            phase,
            result_norm
        FROM {ENRICHED_VIEW_NAME}
        WHERE (%s IS NULL OR ingested_ts > %s)
        ORDER BY ingested_ts ASC, event_ts ASC, sn_global ASC, station_id ASC
        LIMIT %s
    """

    with connection.cursor() as cursor:
        cursor.execute(sql, [last_ingested_ts, last_ingested_ts, limit])
        return dictfetchall(cursor)


def _upsert_board_from_row(row: dict) -> Board:
    serial_number = (row.get("sn_global") or "").strip().upper()
    client_reference = (row.get("reference_client") or "").strip().upper()
    internal_reference = (row.get("reference_interne") or "").strip().upper()

    board, _ = Board.objects.get_or_create(
        serial_number=serial_number,
        defaults={
            "client_reference": client_reference,
            "internal_reference": internal_reference,
            "current_status": Board.Status.HEALTHY,
            "first_seen_at": row["event_ts"],
            "last_seen_at": row["event_ts"],
        },
    )

    changed = False

    if board.client_reference != client_reference:
        board.client_reference = client_reference
        changed = True

    if board.internal_reference != internal_reference:
        board.internal_reference = internal_reference
        changed = True

    if row["event_ts"] < board.first_seen_at:
        board.first_seen_at = row["event_ts"]
        changed = True

    if row["event_ts"] > board.last_seen_at:
        board.last_seen_at = row["event_ts"]
        changed = True

    if changed:
        board.save()

    return board


def _create_test_result_from_row(board: Board, row: dict) -> TestResult:
    source_event_key = build_source_event_key(row)

    test_result, _ = TestResult.objects.get_or_create(
        source_event_key=source_event_key,
        defaults={
            "board": board,
            "serial_number": board.serial_number,
            "client_reference": board.client_reference,
            "internal_reference": board.internal_reference,
            "operator_name": row.get("operator_name") or "",
            "tester_id": row.get("station_id") or "",
            "test_phase": normalize_phase(row.get("phase")),
            "result": normalize_result(row.get("result_norm")),
            "failure_type": row.get("defect_type_norm") or row.get("defect_type") or "",
            "failure_message": row.get("defect_exact_norm") or row.get("defect_message") or "",
            "tested_at": row["event_ts"],
            "raw_ingested_ts": row.get("ingested_ts"),
        },
    )
    return test_result


def _open_failure_if_needed(board: Board, test_result: TestResult):
    if test_result.result not in KO_RESULTS:
        return None

    failure_case, _ = FailureCase.objects.get_or_create(
        source_test_result=test_result,
        defaults={
            "board": board,
            "serial_number": board.serial_number,
            "client_reference": board.client_reference,
            "internal_reference": board.internal_reference,
            "failure_status": FailureCase.Status.IN_DEFECT,
            "detected_in_phase": test_result.test_phase,
            "detected_on_tester": test_result.tester_id,
            "failure_type": test_result.failure_type,
            "failure_message": test_result.failure_message,
            "opened_at": test_result.tested_at,
        },
    )

    if board.current_status != Board.Status.IN_DEFECT:
        board.current_status = Board.Status.IN_DEFECT
        board.save(update_fields=["current_status", "updated_at"])

    get_or_create_open_ticket_for_failure(
        failure_case=failure_case,
        opened_at=test_result.tested_at,
    )

    return failure_case


def _close_failure_if_retest_passed(board: Board, test_result: TestResult):
    if test_result.result != TestResult.Result.PASSED:
        return None

    active_failure = (
        FailureCase.objects.filter(
            board=board,
            failure_status__in=[
                FailureCase.Status.IN_DEFECT,
                FailureCase.Status.IN_REPAIR,
                FailureCase.Status.WAITING_RETEST,
            ],
            detected_in_phase=test_result.test_phase,
        )
        .order_by("-opened_at", "-id")
        .first()
    )

    if active_failure:
        if has_confirmed_repair_workflow(active_failure):
            active_failure.failure_status = FailureCase.Status.REPAIRED
            active_failure.closed_at = test_result.tested_at
            active_failure.save(update_fields=["failure_status", "closed_at", "updated_at"])
            close_tickets_for_repaired_failure(active_failure, closed_at=test_result.tested_at)
            RepairHistory.objects.filter(
                failure_case=active_failure,
                final_outcome__in=["IN_PROGRESS", "WAITING_RETEST"],
            ).update(
                retest_result=TestResult.Result.PASSED,
                final_outcome="REPAIRED",
            )

            board.current_status = Board.Status.REPAIRED
            board.save(update_fields=["current_status", "updated_at"])
            return active_failure

        active_failure.failure_status = FailureCase.Status.INVALIDATED
        active_failure.closed_at = test_result.tested_at
        active_failure.save(update_fields=["failure_status", "closed_at", "updated_at"])
        cancel_tickets_for_invalidated_failure(active_failure, closed_at=test_result.tested_at)
        RepairHistory.objects.filter(
            failure_case=active_failure,
            final_outcome__in=["IN_PROGRESS", "WAITING_RETEST"],
        ).update(
            retest_result=TestResult.Result.PASSED,
            final_outcome="INVALIDATED",
        )

        board.current_status = Board.Status.HEALTHY
        board.save(update_fields=["current_status", "updated_at"])
        return active_failure

    if board.current_status != Board.Status.HEALTHY:
        board.current_status = Board.Status.HEALTHY
        board.save(update_fields=["current_status", "updated_at"])

    return None

def get_or_create_cursor(source_table: str) -> SyncCursor:
    cursor, _ = SyncCursor.objects.get_or_create(
        source_table=source_table,
        defaults={
            "sync_status": SyncCursor.Status.IDLE,
            "rows_processed": 0,
            "error_message": "",
        },
    )
    return cursor


def mark_sync_running(source_table: str) -> SyncCursor:
    cursor = get_or_create_cursor(source_table)
    cursor.sync_status = SyncCursor.Status.RUNNING
    cursor.error_message = ""
    cursor.save(update_fields=["sync_status", "error_message", "updated_at"])
    return cursor


def mark_sync_success(
    source_table: str,
    *,
    last_source_id=None,
    last_source_timestamp=None,
    rows_processed: int = 0,
) -> SyncCursor:
    cursor = get_or_create_cursor(source_table)
    cursor.sync_status = SyncCursor.Status.SUCCESS
    cursor.last_source_id = last_source_id
    cursor.last_source_timestamp = last_source_timestamp
    cursor.last_synced_at = timezone.now()
    cursor.rows_processed = rows_processed
    cursor.error_message = ""
    cursor.save(
        update_fields=[
            "sync_status",
            "last_source_id",
            "last_source_timestamp",
            "last_synced_at",
            "rows_processed",
            "error_message",
            "updated_at",
        ]
    )
    return cursor


def mark_sync_failed(source_table: str, error_message: str) -> SyncCursor:
    cursor = get_or_create_cursor(source_table)
    cursor.sync_status = SyncCursor.Status.FAILED
    cursor.last_synced_at = timezone.now()
    cursor.error_message = error_message[:5000]
    cursor.save(
        update_fields=[
            "sync_status",
            "last_synced_at",
            "error_message",
            "updated_at",
        ]
    )
    return cursor
@transaction.atomic
def sync_from_enriched_view(limit: int = 500):
    source_table = ENRICHED_VIEW_NAME
    cursor = mark_sync_running(source_table)

    rows = fetch_enriched_rows(cursor.last_source_timestamp, limit=limit)

    if not rows:
        mark_sync_success(
            source_table,
            last_source_id=None,
            last_source_timestamp=cursor.last_source_timestamp,
            rows_processed=0,
        )
        return {
            "status": "success",
            "rows_processed": 0,
            "last_source_timestamp": cursor.last_source_timestamp,
        }

    processed = 0
    last_ingested_ts = cursor.last_source_timestamp

    try:
        for row in rows:
            board = _upsert_board_from_row(row)
            test_result = _create_test_result_from_row(board, row)

            if test_result.result in KO_RESULTS:
                _open_failure_if_needed(board, test_result)
            else:
                _close_failure_if_retest_passed(board, test_result)

            processed += 1
            last_ingested_ts = row.get("ingested_ts") or last_ingested_ts

        mark_sync_success(
            source_table,
            last_source_id=None,
            last_source_timestamp=last_ingested_ts,
            rows_processed=processed,
        )

        return {
            "status": "success",
            "rows_processed": processed,
            "last_source_timestamp": last_ingested_ts,
        }

    except Exception as exc:
        mark_sync_failed(source_table, str(exc))
        raise
