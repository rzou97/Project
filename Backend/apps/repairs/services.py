from decimal import Decimal

from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from apps.boards.models import Board
from apps.failures.models import FailureCase
from apps.repairs.models import RepairAction, RepairTicket


OPEN_TICKET_STATUSES = [
    RepairTicket.Status.OPEN,
    RepairTicket.Status.IN_PROGRESS,
    RepairTicket.Status.WAITING_RETEST,
]
REPAIR_CONFIRMED_TICKET_STATUSES = [
    RepairTicket.Status.WAITING_RETEST,
    RepairTicket.Status.CLOSED,
]


def _build_ticket_code(failure_case: FailureCase, cycle_number: int) -> str:
    serial = (failure_case.serial_number or "UNKNOWN").replace(" ", "")
    return f"RT-{serial}-{failure_case.id}-{cycle_number:03d}"


@transaction.atomic
def get_or_create_open_ticket_for_failure(
    failure_case: FailureCase,
    opened_at=None,
) -> tuple[RepairTicket, bool]:
    ticket = (
        RepairTicket.objects.filter(
            failure_case=failure_case,
            ticket_status__in=OPEN_TICKET_STATUSES,
        )
        .order_by("-cycle_number", "-id")
        .first()
    )
    if ticket:
        return ticket, False

    max_cycle = (
        RepairTicket.objects.filter(failure_case=failure_case)
        .aggregate(max_cycle=Max("cycle_number"))
        .get("max_cycle")
        or 0
    )
    next_cycle = max_cycle + 1
    ticket = RepairTicket.objects.create(
        failure_case=failure_case,
        ticket_code=_build_ticket_code(failure_case, next_cycle),
        ticket_status=RepairTicket.Status.OPEN,
        cycle_number=next_cycle,
        opened_at=opened_at or timezone.now(),
    )
    return ticket, True


def _append_repair_history_from_action(repair_action: RepairAction):
    if not repair_action.repair_ticket_id:
        return

    from apps.intelligence.models import RepairHistory

    failure_case = repair_action.failure_case
    source_test_result = failure_case.source_test_result

    if repair_action.action_progress in [RepairAction.Progress.WAITING_RETEST, RepairAction.Progress.DONE]:
        final_outcome = "WAITING_RETEST"
    elif repair_action.action_progress in [RepairAction.Progress.PENDING, RepairAction.Progress.IN_PROGRESS, RepairAction.Progress.WAITING_PARTS]:
        final_outcome = "IN_PROGRESS"
    else:
        final_outcome = "UNKNOWN"

    RepairHistory.objects.create(
        failure_case=failure_case,
        repair_ticket=repair_action.repair_ticket,
        repair_action=repair_action,
        source_test_result=source_test_result,
        serial_number=failure_case.serial_number,
        client_reference=failure_case.client_reference,
        internal_reference=failure_case.internal_reference,
        detected_in_phase=failure_case.detected_in_phase,
        detected_on_tester=failure_case.detected_on_tester,
        failure_type=repair_action.defect_type or failure_case.failure_type,
        failure_message=failure_case.failure_message,
        technician_matricule=getattr(repair_action.technician, "matricule", "") or "",
        detected_cause=repair_action.detected_cause,
        action_taken=repair_action.action_taken,
        retest_result="",
        final_outcome=final_outcome,
        repair_cycle_count=repair_action.repair_ticket.cycle_number,
    )


@transaction.atomic
def apply_repair_workflow(repair_action: RepairAction) -> RepairAction:
    if not repair_action.repair_ticket_id:
        return repair_action

    repair_ticket = repair_action.repair_ticket
    failure_case = repair_ticket.failure_case
    board = failure_case.board
    progress = repair_action.action_progress

    if progress in [
        RepairAction.Progress.PENDING,
        RepairAction.Progress.IN_PROGRESS,
        RepairAction.Progress.WAITING_PARTS,
    ]:
        if repair_ticket.ticket_status != RepairTicket.Status.IN_PROGRESS:
            repair_ticket.ticket_status = RepairTicket.Status.IN_PROGRESS
            repair_ticket.save(update_fields=["ticket_status", "updated_at"])

        if failure_case.failure_status != FailureCase.Status.IN_REPAIR:
            failure_case.failure_status = FailureCase.Status.IN_REPAIR
            failure_case.save(update_fields=["failure_status", "updated_at"])

        if board.current_status != Board.Status.IN_REPAIR:
            board.current_status = Board.Status.IN_REPAIR
            board.save(update_fields=["current_status", "updated_at"])

    elif progress in [RepairAction.Progress.WAITING_RETEST, RepairAction.Progress.DONE]:
        if repair_ticket.ticket_status != RepairTicket.Status.WAITING_RETEST:
            repair_ticket.ticket_status = RepairTicket.Status.WAITING_RETEST
            repair_ticket.save(update_fields=["ticket_status", "updated_at"])

        if failure_case.failure_status != FailureCase.Status.WAITING_RETEST:
            failure_case.failure_status = FailureCase.Status.WAITING_RETEST
            failure_case.save(update_fields=["failure_status", "updated_at"])

        if board.current_status != Board.Status.WAITING_RETEST:
            board.current_status = Board.Status.WAITING_RETEST
            board.save(update_fields=["current_status", "updated_at"])

    _append_repair_history_from_action(repair_action)

    from apps.intelligence.services import AiRepairAdvisor

    AiRepairAdvisor.score_repair_effectiveness(repair_ticket)
    return repair_action


@transaction.atomic
def apply_repair_ticket_workflow(repair_ticket: RepairTicket) -> RepairTicket:
    failure_case = repair_ticket.failure_case
    board = failure_case.board
    status = repair_ticket.ticket_status

    if status in [RepairTicket.Status.OPEN, RepairTicket.Status.IN_PROGRESS]:
        if failure_case.failure_status not in [
            FailureCase.Status.REPAIRED,
            FailureCase.Status.INVALIDATED,
        ]:
            failure_case.failure_status = FailureCase.Status.IN_REPAIR
            failure_case.save(update_fields=["failure_status", "updated_at"])

        if board.current_status != Board.Status.IN_REPAIR:
            board.current_status = Board.Status.IN_REPAIR
            board.save(update_fields=["current_status", "updated_at"])

    elif status == RepairTicket.Status.WAITING_RETEST:
        if failure_case.failure_status not in [
            FailureCase.Status.REPAIRED,
            FailureCase.Status.INVALIDATED,
        ]:
            failure_case.failure_status = FailureCase.Status.WAITING_RETEST
            failure_case.save(update_fields=["failure_status", "updated_at"])

        if board.current_status != Board.Status.WAITING_RETEST:
            board.current_status = Board.Status.WAITING_RETEST
            board.save(update_fields=["current_status", "updated_at"])

    elif status == RepairTicket.Status.CANCELLED:
        if failure_case.failure_status != FailureCase.Status.INVALIDATED:
            failure_case.failure_status = FailureCase.Status.INVALIDATED
            failure_case.closed_at = repair_ticket.closed_at or timezone.now()
            failure_case.save(update_fields=["failure_status", "closed_at", "updated_at"])

        if board.current_status != Board.Status.HEALTHY:
            board.current_status = Board.Status.HEALTHY
            board.save(update_fields=["current_status", "updated_at"])

    return repair_ticket


def has_confirmed_repair_workflow(failure_case: FailureCase) -> bool:
    return RepairTicket.objects.filter(
        failure_case=failure_case,
        ticket_status__in=REPAIR_CONFIRMED_TICKET_STATUSES,
        repair_actions__isnull=False,
    ).exists()


@transaction.atomic
def close_tickets_for_repaired_failure(failure_case: FailureCase, closed_at=None):
    closed_at = closed_at or timezone.now()

    tickets = RepairTicket.objects.filter(
        failure_case=failure_case,
        ticket_status__in=OPEN_TICKET_STATUSES,
    )

    for ticket in tickets:
        ticket.ticket_status = RepairTicket.Status.CLOSED
        ticket.closed_at = closed_at
        if ticket.repair_effectiveness is None:
            ticket.repair_effectiveness = Decimal("100.00")
        ticket.save(update_fields=["ticket_status", "closed_at", "repair_effectiveness", "updated_at"])


@transaction.atomic
def cancel_tickets_for_invalidated_failure(failure_case: FailureCase, closed_at=None):
    closed_at = closed_at or timezone.now()

    tickets = RepairTicket.objects.filter(
        failure_case=failure_case,
        ticket_status__in=OPEN_TICKET_STATUSES,
    )

    for ticket in tickets:
        ticket.ticket_status = RepairTicket.Status.CANCELLED
        ticket.closed_at = closed_at
        ticket.save(update_fields=["ticket_status", "closed_at", "updated_at"])
