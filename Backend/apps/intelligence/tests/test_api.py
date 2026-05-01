from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.boards.models import Board
from apps.failures.models import FailureCase
from apps.intelligence.models import RepairHistory
from apps.repairs.models import RepairTicket
from apps.testresults.models import TestResult


class FailureIntelligenceApiTests(APITestCase):
    def setUp(self):
        now = timezone.now()
        self.user = User.objects.create_user(
            email="intelligence-api@atems.tn",
            password="secret123",
            first_name="Intel",
            last_name="Api",
            matricule="INTAPI01",
            role=User.Role.ADMIN,
            email_verified=True,
        )
        self.board = Board.objects.create(
            serial_number="SN-INT-API-001",
            client_reference="REF-INT-API",
            internal_reference="INT-INT-API",
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
            tester_id="TESTER-INT-API",
            test_phase=TestResult.Phase.BOARD_TEST,
            result=TestResult.Result.FAILED,
            failure_type="PRIMARY",
            failure_message="MESURE 15VP PRIMAIRE = 0V",
            tested_at=now,
            source_event_key="intel-api-failed",
        )
        self.failure_case = FailureCase.objects.create(
            board=self.board,
            source_test_result=self.failed_result,
            serial_number=self.board.serial_number,
            client_reference=self.board.client_reference,
            internal_reference=self.board.internal_reference,
            failure_status=FailureCase.Status.IN_DEFECT,
            detected_in_phase=TestResult.Phase.BOARD_TEST,
            detected_on_tester="TESTER-INT-API",
            failure_type="PRIMARY",
            failure_message="MESURE 15VP PRIMAIRE = 0V",
            opened_at=now,
        )
        self.ticket = RepairTicket.objects.create(
            failure_case=self.failure_case,
            ticket_code="RT-SN-INT-API-001-001",
            ticket_status=RepairTicket.Status.OPEN,
            cycle_number=1,
            opened_at=now,
        )
        RepairHistory.objects.create(
            failure_case=self.failure_case,
            repair_ticket=self.ticket,
            serial_number="SN-HIST-INT-001",
            client_reference=self.board.client_reference,
            internal_reference=self.board.internal_reference,
            detected_in_phase=TestResult.Phase.BOARD_TEST,
            detected_on_tester="TESTER-INT-API",
            failure_type="PRIMARY",
            failure_message="MESURE 15VP PRIMAIRE = 0V",
            technician_matricule="TECH-INT-001",
            detected_cause="RG2 HS",
            action_taken="Remplacement RG2",
            retest_result=TestResult.Result.PASSED,
            final_outcome="REPAIRED",
            repair_cycle_count=1,
        )

    def test_can_trigger_manual_failure_analysis(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(
          reverse("intelligence-failure-enrichments-analyze"),
          {
              "failure_case": self.failure_case.id,
              "repair_ticket": self.ticket.id,
          },
          format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["enrichment"]["failure_case"], self.failure_case.id)
        self.assertEqual(response.data["prediction"]["repair_ticket"], self.ticket.id)
