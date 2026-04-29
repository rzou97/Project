from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import User
from apps.boards.models import Board
from apps.failures.models import FailureCase
from apps.repairs.models import RepairAction, RepairTicket
from apps.syncengine.services import _close_failure_if_retest_passed
from apps.testresults.models import TestResult


class RetestClosureWorkflowTests(TestCase):
    def setUp(self):
        now = timezone.now()
        self.board = Board.objects.create(
            serial_number="SN-001",
            client_reference="REF-1",
            internal_reference="INT-1",
            current_status=Board.Status.IN_DEFECT,
            first_seen_at=now,
            last_seen_at=now,
        )
        self.failed_result = TestResult.objects.create(
            board=self.board,
            serial_number=self.board.serial_number,
            client_reference=self.board.client_reference,
            internal_reference=self.board.internal_reference,
            operator_name="OPERATEUR",
            tester_id="TESTER-A",
            test_phase=TestResult.Phase.BOARD_TEST,
            result=TestResult.Result.FAILED,
            failure_type="POWERON",
            failure_message="IBAT",
            tested_at=now,
            source_event_key="failed-key",
        )
        self.failure_case = FailureCase.objects.create(
            board=self.board,
            source_test_result=self.failed_result,
            serial_number=self.board.serial_number,
            client_reference=self.board.client_reference,
            internal_reference=self.board.internal_reference,
            failure_status=FailureCase.Status.IN_DEFECT,
            detected_in_phase=TestResult.Phase.BOARD_TEST,
            detected_on_tester="TESTER-A",
            failure_type="POWERON",
            failure_message="IBAT",
            opened_at=now,
        )

    def _build_pass_result(self, key: str = "pass-key") -> TestResult:
        return TestResult.objects.create(
            board=self.board,
            serial_number=self.board.serial_number,
            client_reference=self.board.client_reference,
            internal_reference=self.board.internal_reference,
            operator_name="OPERATEUR",
            tester_id="TESTER-A",
            test_phase=TestResult.Phase.BOARD_TEST,
            result=TestResult.Result.PASSED,
            failure_type="",
            failure_message="",
            tested_at=timezone.now(),
            source_event_key=key,
        )

    def test_pass_without_technician_action_invalidates_false_failure(self):
        ticket = RepairTicket.objects.create(
            failure_case=self.failure_case,
            ticket_code="RT-SN-001-1-001",
            ticket_status=RepairTicket.Status.OPEN,
            cycle_number=1,
            opened_at=timezone.now(),
        )
        pass_result = self._build_pass_result("pass-no-repair")

        _close_failure_if_retest_passed(self.board, pass_result)

        self.failure_case.refresh_from_db()
        self.board.refresh_from_db()
        ticket.refresh_from_db()

        self.assertEqual(self.failure_case.failure_status, FailureCase.Status.INVALIDATED)
        self.assertEqual(self.board.current_status, Board.Status.HEALTHY)
        self.assertEqual(ticket.ticket_status, RepairTicket.Status.CANCELLED)
        self.assertIsNotNone(ticket.closed_at)

    def test_pass_after_repair_action_marks_failure_as_repaired(self):
        technician = User.objects.create_user(
            email="tech@atems.tn",
            password="secret123",
            first_name="Tech",
            last_name="One",
            matricule="TECH001",
            role=User.Role.REPAIR_TECHNICIAN,
            email_verified=True,
        )
        ticket = RepairTicket.objects.create(
            failure_case=self.failure_case,
            ticket_code="RT-SN-001-1-002",
            ticket_status=RepairTicket.Status.WAITING_RETEST,
            cycle_number=1,
            opened_at=timezone.now(),
        )
        RepairAction.objects.create(
            repair_ticket=ticket,
            technician=technician,
            defect_type="POWERON",
            observed_defect="IBAT",
            detected_cause="Loose connector",
            action_taken="Reconnect and secure",
            action_progress=RepairAction.Progress.WAITING_RETEST,
            performed_at=timezone.now(),
        )
        pass_result = self._build_pass_result("pass-after-repair")

        _close_failure_if_retest_passed(self.board, pass_result)

        self.failure_case.refresh_from_db()
        self.board.refresh_from_db()
        ticket.refresh_from_db()

        self.assertEqual(self.failure_case.failure_status, FailureCase.Status.REPAIRED)
        self.assertEqual(self.board.current_status, Board.Status.REPAIRED)
        self.assertEqual(ticket.ticket_status, RepairTicket.Status.CLOSED)
        self.assertIsNotNone(ticket.closed_at)
