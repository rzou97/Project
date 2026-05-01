from django.test import TestCase
from django.utils import timezone

from apps.boards.models import Board
from apps.failures.models import FailureCase
from apps.intelligence.models import FailureEnrichment, RepairHistory, RepairProcedureTemplate
from apps.intelligence.services import FailureIntelligenceService
from apps.intelligence.tasks import analyze_failure_case_task
from apps.repairs.models import RepairTicket
from apps.testresults.models import TestResult


class FailureIntelligenceServiceTests(TestCase):
    def setUp(self):
        now = timezone.now()
        self.board = Board.objects.create(
            serial_number="SN-IA-001",
            client_reference="REF-IA-01",
            internal_reference="INT-IA-01",
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
            tester_id="TESTER-IA",
            test_phase=TestResult.Phase.BOARD_TEST,
            result=TestResult.Result.FAILED,
            failure_type="PRIMARY",
            failure_message="MESURE 15VP PRIMAIRE = 0V",
            tested_at=now,
            source_event_key="ia-failed-source",
        )
        self.failure_case = FailureCase.objects.create(
            board=self.board,
            source_test_result=self.failed_result,
            serial_number=self.board.serial_number,
            client_reference=self.board.client_reference,
            internal_reference=self.board.internal_reference,
            failure_status=FailureCase.Status.IN_DEFECT,
            detected_in_phase=TestResult.Phase.BOARD_TEST,
            detected_on_tester="TESTER-IA",
            failure_type="PRIMARY",
            failure_message="MESURE 15VP PRIMAIRE = 0V",
            opened_at=now,
        )
        self.ticket = RepairTicket.objects.create(
            failure_case=self.failure_case,
            ticket_code="RT-SN-IA-001-0001",
            ticket_status=RepairTicket.Status.OPEN,
            cycle_number=1,
            opened_at=now,
        )
        self.history_board = Board.objects.create(
            serial_number="SN-HIST-001",
            client_reference="REF-IA-01",
            internal_reference="INT-IA-01",
            current_status=Board.Status.REPAIRED,
            first_seen_at=now,
            last_seen_at=now,
        )
        self.history_result = TestResult.objects.create(
            board=self.history_board,
            serial_number=self.history_board.serial_number,
            client_reference=self.history_board.client_reference,
            internal_reference=self.history_board.internal_reference,
            operator_name="OPERATEUR",
            tester_id="TESTER-IA",
            test_phase=TestResult.Phase.BOARD_TEST,
            result=TestResult.Result.FAILED,
            failure_type="PRIMARY",
            failure_message="MESURE 15VP PRIMAIRE = 0V",
            tested_at=now,
            source_event_key="ia-history-source",
        )
        self.history_failure_case = FailureCase.objects.create(
            board=self.history_board,
            source_test_result=self.history_result,
            serial_number=self.history_board.serial_number,
            client_reference=self.history_board.client_reference,
            internal_reference=self.history_board.internal_reference,
            failure_status=FailureCase.Status.REPAIRED,
            detected_in_phase=TestResult.Phase.BOARD_TEST,
            detected_on_tester="TESTER-IA",
            failure_type="PRIMARY",
            failure_message="MESURE 15VP PRIMAIRE = 0V",
            opened_at=now,
            closed_at=now,
        )
        self.history_ticket = RepairTicket.objects.create(
            failure_case=self.history_failure_case,
            ticket_code="RT-SN-HIST-001-0001",
            ticket_status=RepairTicket.Status.CLOSED,
            cycle_number=1,
            opened_at=now,
            closed_at=now,
            repair_effectiveness="100.00",
        )
        RepairProcedureTemplate.objects.create(
            procedure_name="PROC_PRIMARY_V1",
            failure_type="PRIMARY",
            failure_signature="PRIMARY 15VP 0V",
            recommended_steps=["Verifier RG2", "Mesurer la ligne primaire"],
            recommended_parts=["RG2"],
            success_rate="87.50",
            version="v1",
            generated_at=now,
        )
        RepairHistory.objects.create(
            failure_case=self.history_failure_case,
            repair_ticket=self.history_ticket,
            serial_number=self.history_board.serial_number,
            client_reference="REF-IA-01",
            internal_reference="INT-IA-01",
            detected_in_phase=TestResult.Phase.BOARD_TEST,
            detected_on_tester="TESTER-IA",
            failure_type="PRIMARY",
            failure_message="MESURE 15VP PRIMAIRE = 0V",
            technician_matricule="TECH-001",
            detected_cause="RG2 HS",
            action_taken="Remplacement RG2",
            retest_result=TestResult.Result.PASSED,
            final_outcome="REPAIRED",
            repair_cycle_count=1,
        )
        RepairHistory.objects.create(
            failure_case=self.history_failure_case,
            repair_ticket=self.history_ticket,
            serial_number=self.history_board.serial_number,
            client_reference="REF-IA-01",
            internal_reference="INT-IA-01",
            detected_in_phase=TestResult.Phase.BOARD_TEST,
            detected_on_tester="TESTER-IA",
            failure_type="PRIMARY",
            failure_message="MESURE 15VP PRIMAIRE = 0V",
            technician_matricule="TECH-002",
            detected_cause="RG2 HS",
            action_taken="Remplacement RG2",
            retest_result=TestResult.Result.PASSED,
            final_outcome="REPAIRED",
            repair_cycle_count=1,
        )

    def test_analyze_failure_case_creates_enrichment_and_prediction(self):
        enrichment, prediction = FailureIntelligenceService.analyze_failure_case(
            self.failure_case,
            self.ticket,
        )

        self.assertEqual(enrichment.failure_case, self.failure_case)
        self.assertEqual(enrichment.normalized_family, "PRIMARY")
        self.assertEqual(enrichment.probable_root_cause, "RG2 HS")
        self.assertEqual(enrichment.suggested_action, "Remplacement RG2")
        self.assertIn("RG2", enrichment.suspect_components)
        self.assertEqual(enrichment.enrichment_source, FailureEnrichment.Source.HYBRID)
        self.assertGreaterEqual(enrichment.supporting_history_count, 2)
        self.assertFalse(enrichment.needs_human_review)

        self.assertEqual(prediction.failure_case, self.failure_case)
        self.assertEqual(prediction.repair_ticket, self.ticket)
        self.assertEqual(prediction.predicted_cause, "RG2 HS")
        self.assertEqual(prediction.recommended_action, "Remplacement RG2")
        self.assertEqual(prediction.prediction_source, FailureEnrichment.Source.HYBRID)
        self.assertGreater(prediction.confidence_score, 0)

    def test_analyze_failure_case_task_returns_created_ids(self):
        result = analyze_failure_case_task(self.failure_case.id, self.ticket.id)

        self.assertEqual(result["failure_case_id"], self.failure_case.id)
        self.assertEqual(result["repair_ticket_id"], self.ticket.id)
        self.assertTrue(result["enrichment_id"])
        self.assertTrue(result["prediction_id"])
