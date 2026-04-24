from decimal import Decimal, ROUND_HALF_UP

from django.utils import timezone

from apps.alerts.models import AlertEvent, AlertRule
from apps.maintenance.models import CurativeTicket
from apps.testresults.models import TestResult


OPEN_ALERT_STATUSES = [AlertEvent.Status.OPEN, AlertEvent.Status.ACKNOWLEDGED]
OPEN_TICKET_STATUSES = [
    CurativeTicket.Status.OPEN,
    CurativeTicket.Status.IN_PROGRESS,
    CurativeTicket.Status.WAITING_VALIDATION,
]


def _round_2(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _start_of_today():
    now = timezone.localtime()
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def _one_hour_ago():
    return timezone.now() - timezone.timedelta(hours=1)


def _get_all_relevant_tester_ids():
    start_today = _start_of_today()

    tester_ids_today = list(
        TestResult.objects.filter(tested_at__gte=start_today)
        .exclude(tester_id="")
        .values_list("tester_id", flat=True)
        .distinct()
    )

    tester_ids_with_open_tickets = list(
        CurativeTicket.objects.filter(status__in=OPEN_TICKET_STATUSES)
        .exclude(asset__tester_id="")
        .values_list("asset__tester_id", flat=True)
        .distinct()
    )

    tester_ids = sorted(set(tester_ids_today + tester_ids_with_open_tickets))
    return tester_ids


def get_testers_fpy_instant():
    start_today = _start_of_today()
    tester_ids = _get_all_relevant_tester_ids()

    data = []

    for tester_id in tester_ids:
        qs = TestResult.objects.filter(
            tester_id=tester_id,
            tested_at__gte=start_today,
        )

        unique_sn_tested = qs.values("serial_number").distinct().count()

        unique_sn_passed = (
            qs.filter(result=TestResult.Result.PASSED)
            .values("serial_number")
            .distinct()
            .count()
        )

        last_test = qs.order_by("-tested_at", "-id").first()

        if unique_sn_tested > 0:
            fpy_instant = _round_2(
                (Decimal(unique_sn_passed) / Decimal(unique_sn_tested)) * Decimal("100")
            )
        else:
            fpy_instant = Decimal("0.00")

        data.append(
            {
                "tester_id": tester_id,
                "day_date": timezone.localdate(),
                "unique_sn_tested": unique_sn_tested,
                "unique_sn_passed": unique_sn_passed,
                "fpy_instant": fpy_instant,
                "last_test_at": last_test.tested_at if last_test else None,
            }
        )

    return data


def _get_current_fail_rate(tester_id: str) -> Decimal:
    since = _one_hour_ago()
    qs = TestResult.objects.filter(tester_id=tester_id, tested_at__gte=since)

    total = qs.count()
    if total == 0:
        return Decimal("0.00")

    failed = qs.filter(result=TestResult.Result.FAILED).count()
    return _round_2((Decimal(failed) / Decimal(total)) * Decimal("100"))


def _has_repeated_last_three_defects(tester_id: str) -> bool:
    last_three = list(
        TestResult.objects.filter(tester_id=tester_id)
        .order_by("-tested_at", "-id")[:3]
    )

    if len(last_three) < 3:
        return False

    messages = [(item.failure_message or "").strip() for item in last_three]
    if not messages[0]:
        return False

    return len(set(messages)) == 1


def _get_open_alerts_for_tester(tester_id: str):
    return AlertEvent.objects.filter(
        entity_key=tester_id,
        status__in=OPEN_ALERT_STATUSES,
    ).select_related("rule")


def _get_alert_status(open_alerts):
    alert_types = sorted({item.rule.alert_type for item in open_alerts})

    if not alert_types:
        return "NONE"

    if len(alert_types) > 1:
        return "MULTIPLE"

    only_type = alert_types[0]

    if only_type == AlertRule.AlertType.HIGH_FAILURE_RATE:
        return "OPEN_HIGH_FAIL_RATE"
    if only_type == AlertRule.AlertType.REPEATED_DEFECT_MESSAGE:
        return "OPEN_REPEATED_DEFECT"
    if only_type == AlertRule.AlertType.LOW_FPY:
        return "OPEN_LOW_FPY"

    return "OPEN_ALERT"


def _get_current_status(tester_id: str, fail_rate: Decimal, has_repeated_defect: bool, has_open_ticket: bool):
    if has_open_ticket:
        return "IN_REPAIR"
    if has_repeated_defect:
        return "STOPPED"
    if fail_rate > Decimal("20"):
        return "DEGRADED"
    return "ACTIVE"


def get_testers_current_status():
    tester_ids = _get_all_relevant_tester_ids()
    since = _one_hour_ago()

    data = []

    for tester_id in tester_ids:
        latest_test = (
            TestResult.objects.filter(tester_id=tester_id)
            .order_by("-tested_at", "-id")
            .first()
        )

        if not latest_test:
            continue

        current_hour_qs = TestResult.objects.filter(
            tester_id=tester_id,
            tested_at__gte=since,
        )

        total_tests_current_hour = current_hour_qs.count()
        failed_tests_current_hour = current_hour_qs.filter(
            result=TestResult.Result.FAILED
        ).count()

        fail_rate = _get_current_fail_rate(tester_id)
        has_repeated_defect = _has_repeated_last_three_defects(tester_id)

        open_ticket_count = CurativeTicket.objects.filter(
            asset__tester_id=tester_id,
            status__in=OPEN_TICKET_STATUSES,
        ).count()

        open_alerts = list(_get_open_alerts_for_tester(tester_id))
        open_alert_count = len(open_alerts)
        open_alert_types = sorted({item.rule.alert_type for item in open_alerts})

        current_status = _get_current_status(
            tester_id=tester_id,
            fail_rate=fail_rate,
            has_repeated_defect=has_repeated_defect,
            has_open_ticket=open_ticket_count > 0,
        )

        data.append(
            {
                "tester_id": tester_id,
                "operator_name": latest_test.operator_name,
                "internal_reference": latest_test.internal_reference,
                "last_test_at": latest_test.tested_at,
                "current_fail_rate": fail_rate,
                "current_status": current_status,
                "alert_status": _get_alert_status(open_alerts),
                "open_alert_count": open_alert_count,
                "open_alert_types": open_alert_types,
                "total_tests_current_hour": total_tests_current_hour,
                "failed_tests_current_hour": failed_tests_current_hour,
            }
        )

    data.sort(key=lambda x: x["tester_id"])
    return data


class KpiService:
    @staticmethod
    def get_testers_fpy_instant():
        return get_testers_fpy_instant()

    @staticmethod
    def get_testers_current_status():
        return get_testers_current_status()
