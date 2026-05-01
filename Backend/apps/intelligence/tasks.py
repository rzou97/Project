from celery import shared_task

from apps.intelligence.services import FailureIntelligenceService


@shared_task
def analyze_failure_case_task(failure_case_id: int, repair_ticket_id: int | None = None):
    enrichment, prediction = FailureIntelligenceService.analyze_failure_case_by_id(
        failure_case_id=failure_case_id,
        repair_ticket_id=repair_ticket_id,
    )
    return {
        "failure_case_id": failure_case_id,
        "repair_ticket_id": repair_ticket_id,
        "enrichment_id": enrichment.id,
        "prediction_id": prediction.id,
        "confidence_score": str(prediction.confidence_score),
    }
