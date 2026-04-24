from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.intelligence.filters import (
    RepairHistoryFilter,
    RepairPredictionFilter,
    RepairProcedureTemplateFilter,
)
from apps.intelligence.models import RepairHistory, RepairPrediction, RepairProcedureTemplate

from .serializers import (
    RepairHistorySerializer,
    RepairPredictionSerializer,
    RepairProcedureTemplateSerializer,
)


class RepairHistoryViewSet(ReadOnlyModelViewSet):
    queryset = RepairHistory.objects.select_related(
        "failure_case",
        "repair_ticket",
        "repair_action",
        "source_test_result",
    ).all()
    serializer_class = RepairHistorySerializer
    permission_classes = [IsAuthenticated]
    filterset_class = RepairHistoryFilter
    search_fields = [
        "serial_number",
        "client_reference",
        "internal_reference",
        "failure_type",
        "failure_message",
        "detected_on_tester",
        "technician_matricule",
        "detected_cause",
        "action_taken",
        "repair_ticket__ticket_code",
    ]
    ordering_fields = ["created_at", "repair_cycle_count"]
    ordering = ["-created_at", "-id"]


class RepairProcedureTemplateViewSet(ReadOnlyModelViewSet):
    queryset = RepairProcedureTemplate.objects.all()
    serializer_class = RepairProcedureTemplateSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = RepairProcedureTemplateFilter
    search_fields = ["procedure_name", "failure_type", "failure_signature", "version"]
    ordering_fields = ["generated_at", "success_rate", "version"]
    ordering = ["-generated_at", "-id"]


class RepairPredictionViewSet(ReadOnlyModelViewSet):
    queryset = RepairPrediction.objects.select_related("recommended_procedure").all()
    serializer_class = RepairPredictionSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = RepairPredictionFilter
    search_fields = [
        "prediction_type",
        "target_serial_number",
        "predicted_cause",
        "recommended_action",
        "recommended_procedure__procedure_name",
    ]
    ordering_fields = ["predicted_at", "created_at", "confidence_score"]
    ordering = ["-predicted_at", "-id"]
