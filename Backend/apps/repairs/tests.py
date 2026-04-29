from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.boards.models import Board
from apps.failures.models import FailureCase
from apps.repairs.models import RepairAction, RepairTicket
from apps.testresults.models import TestResult


class RepairActionApiTests(APITestCase):
    def setUp(self):
        now = timezone.now()
        self.technician = User.objects.create_user(
            email="tech-api@atems.tn",
            password="secret123",
            first_name="Tech",
            last_name="Api",
            matricule="TECHAPI01",
            role=User.Role.REPAIR_TECHNICIAN,
            email_verified=True,
        )
        self.board = Board.objects.create(
            serial_number="SN-API-001",
            client_reference="REF-API-01",
            internal_reference="INT-API-01",
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
            tester_id="TESTER-API",
            test_phase=TestResult.Phase.BOARD_TEST,
            result=TestResult.Result.FAILED,
            failure_type="PRIMARY",
            failure_message="PRIMARY 15VP",
            tested_at=now,
            source_event_key="repair-api-failed",
        )
        self.failure_case = FailureCase.objects.create(
            board=self.board,
            source_test_result=self.failed_result,
            serial_number=self.board.serial_number,
            client_reference=self.board.client_reference,
            internal_reference=self.board.internal_reference,
            failure_status=FailureCase.Status.IN_DEFECT,
            detected_in_phase=TestResult.Phase.BOARD_TEST,
            detected_on_tester="TESTER-API",
            failure_type="PRIMARY",
            failure_message="PRIMARY 15VP",
            opened_at=now,
        )
        self.ticket = RepairTicket.objects.create(
            failure_case=self.failure_case,
            ticket_code="RT-SN-API-001-1-001",
            ticket_status=RepairTicket.Status.OPEN,
            cycle_number=1,
            opened_at=now,
        )

    def test_create_repair_action_returns_created_response(self):
        self.client.force_authenticate(self.technician)

        response = self.client.post(
            reverse("repair-actions-list"),
            {
                "repair_ticket": self.ticket.id,
                "defect_type": "PRIMARY",
                "observed_defect": "MESURE 15VP = 0V",
                "detected_cause": "RG2 HS",
                "action_taken": "Remplacement RG2",
                "action_progress": RepairAction.Progress.WAITING_RETEST,
                "performed_at": timezone.now().isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["ticket_code"], self.ticket.ticket_code)
        self.assertEqual(response.data["serial_number"], self.ticket.failure_case.serial_number)
        self.assertEqual(response.data["action_progress"], RepairAction.Progress.WAITING_RETEST)

        self.ticket.refresh_from_db()
        self.failure_case.refresh_from_db()
        self.board.refresh_from_db()

        self.assertEqual(self.ticket.ticket_status, RepairTicket.Status.WAITING_RETEST)
        self.assertEqual(self.failure_case.failure_status, FailureCase.Status.WAITING_RETEST)
        self.assertEqual(self.board.current_status, Board.Status.WAITING_RETEST)
