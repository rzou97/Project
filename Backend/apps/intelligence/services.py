from decimal import Decimal

from django.db.models import Count
from django.utils import timezone

from apps.failures.models import FailureCase
from apps.repairs.models import RepairTicket

from .models import RepairHistory, RepairPrediction, RepairProcedureTemplate


class AiRepairAdvisor:
    @staticmethod
    def buildRepairProcedure(failure_type: str, failure_signature: str = ""):
        return AiRepairAdvisor.build_repair_procedure(failure_type=failure_type, failure_signature=failure_signature)

    @staticmethod
    def predictRepair(failure_case: FailureCase, repair_ticket: RepairTicket | None = None):
        return AiRepairAdvisor.predict_repair(failure_case=failure_case, repair_ticket=repair_ticket)

    @staticmethod
    def scoreRepairEffectiveness(repair_ticket: RepairTicket):
        return AiRepairAdvisor.score_repair_effectiveness(repair_ticket=repair_ticket)

    @staticmethod
    def suggestParts(failure_type: str):
        return AiRepairAdvisor.suggest_parts(failure_type=failure_type)

    @staticmethod
    def build_repair_procedure(failure_type: str, failure_signature: str = "") -> RepairProcedureTemplate:
        histories = RepairHistory.objects.filter(failure_type__iexact=failure_type)
        if failure_signature:
            histories = histories.filter(failure_message__icontains=failure_signature)

        actions = list(
            histories.exclude(action_taken="")
            .values_list("action_taken", flat=True)
            .distinct()[:5]
        )
        causes = list(
            histories.exclude(detected_cause="")
            .values_list("detected_cause", flat=True)
            .distinct()[:5]
        )

        total = histories.count()
        repaired = histories.filter(final_outcome__iexact="REPAIRED").count()
        success_rate = Decimal("0.00")
        if total > 0:
            success_rate = (Decimal(repaired) / Decimal(total)) * Decimal("100")

        existing_versions = RepairProcedureTemplate.objects.filter(failure_type__iexact=failure_type).count()
        version = f"v{existing_versions + 1}"

        return RepairProcedureTemplate.objects.create(
            procedure_name=f"PROC_{failure_type}_{version}",
            failure_type=failure_type,
            failure_signature=failure_signature or "",
            recommended_steps=actions if actions else causes,
            recommended_parts=[],
            success_rate=success_rate.quantize(Decimal("0.01")),
            version=version,
            generated_at=timezone.now(),
        )

    @staticmethod
    def predict_repair(failure_case: FailureCase, repair_ticket: RepairTicket | None = None) -> RepairPrediction:
        histories = RepairHistory.objects.filter(failure_type__iexact=failure_case.failure_type)

        top_cause = (
            histories.exclude(detected_cause="")
            .values("detected_cause")
            .annotate(total=Count("id"))
            .order_by("-total")
            .first()
        )
        predicted_cause = top_cause["detected_cause"] if top_cause else ""

        template = (
            RepairProcedureTemplate.objects.filter(failure_type__iexact=failure_case.failure_type)
            .order_by("-generated_at", "-id")
            .first()
        )
        recommended_action = ""
        if template and template.recommended_steps:
            recommended_action = str(template.recommended_steps[0])

        confidence_score = Decimal("0.5000")
        history_count = histories.count()
        if history_count > 0:
            confidence_score = min(Decimal("0.9900"), Decimal("0.5000") + (Decimal(history_count) / Decimal("200")))

        return RepairPrediction.objects.create(
            prediction_type="REPAIR_CAUSE",
            target_serial_number=failure_case.serial_number,
            predicted_cause=predicted_cause,
            recommended_action=recommended_action,
            recommended_procedure=template,
            confidence_score=confidence_score,
            predicted_at=timezone.now(),
        )

    @staticmethod
    def score_repair_effectiveness(repair_ticket: RepairTicket) -> Decimal:
        latest_history = (
            RepairHistory.objects.filter(repair_ticket=repair_ticket)
            .order_by("-created_at", "-id")
            .first()
        )

        score = Decimal("50.00")
        if latest_history:
            if latest_history.final_outcome.upper() == "REPAIRED":
                score = Decimal("100.00")
            elif latest_history.final_outcome.upper() == "WAITING_RETEST":
                score = Decimal("75.00")
            elif latest_history.final_outcome.upper() == "IN_PROGRESS":
                score = Decimal("50.00")

        repair_ticket.repair_effectiveness = score
        repair_ticket.save(update_fields=["repair_effectiveness", "updated_at"])
        return score

    @staticmethod
    def suggest_parts(failure_type: str) -> list:
        template = (
            RepairProcedureTemplate.objects.filter(failure_type__iexact=failure_type)
            .exclude(recommended_parts=[])
            .order_by("-generated_at", "-id")
            .first()
        )
        if not template:
            return []
        return template.recommended_parts
