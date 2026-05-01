from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.intelligence.filters import (
    FailureEnrichmentFilter,
    RepairHistoryFilter,
    RepairPredictionFilter,
    RepairProcedureTemplateFilter,
)
from apps.intelligence.models import (
    FailureEnrichment,
    RepairHistory,
    RepairPrediction,
    RepairProcedureTemplate,
)
from apps.intelligence.services import FailureIntelligenceService
from common.pagination import StandardResultsSetPagination

from .serializers import (
    FailureAnalysisRequestSerializer,
    FailureAnalysisResponseSerializer,
    FailureEnrichmentSerializer,
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
    pagination_class = StandardResultsSetPagination
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
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]
    filterset_class = RepairProcedureTemplateFilter
    search_fields = ["procedure_name", "failure_type", "failure_signature", "version"]
    ordering_fields = ["generated_at", "success_rate", "version"]
    ordering = ["-generated_at", "-id"]


class FailureEnrichmentViewSet(ReadOnlyModelViewSet):
    queryset = FailureEnrichment.objects.select_related("failure_case").all()
    serializer_class = FailureEnrichmentSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]
    filterset_class = FailureEnrichmentFilter
    search_fields = [
        "failure_case__serial_number",
        "failure_case__client_reference",
        "failure_case__internal_reference",
        "failure_case__failure_type",
        "failure_case__failure_message",
        "normalized_family",
        "normalized_signature",
        "probable_root_cause",
        "suggested_action",
    ]
    ordering_fields = ["enriched_at", "confidence_score", "supporting_history_count"]
    ordering = ["-enriched_at", "-id"]

    @action(detail=False, methods=["post"], url_path="analyze")
    def analyze(self, request, *args, **kwargs):
        request_serializer = FailureAnalysisRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        failure_case = request_serializer.validated_data["failure_case"]
        repair_ticket = request_serializer.validated_data.get("repair_ticket")

        enrichment, prediction = FailureIntelligenceService.analyze_failure_case(
            failure_case=failure_case,
            repair_ticket=repair_ticket,
        )
        response_serializer = FailureAnalysisResponseSerializer(
            {
                "enrichment": enrichment,
                "prediction": prediction,
            }
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class RepairPredictionViewSet(ReadOnlyModelViewSet):
    queryset = RepairPrediction.objects.select_related(
        "recommended_procedure",
        "failure_case",
        "repair_ticket",
    ).all()
    serializer_class = RepairPredictionSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]
    filterset_class = RepairPredictionFilter
    search_fields = [
        "prediction_type",
        "prediction_source",
        "target_serial_number",
        "predicted_cause",
        "recommended_action",
        "input_signature",
        "recommended_procedure__procedure_name",
    ]
    ordering_fields = ["predicted_at", "created_at", "confidence_score"]
    ordering = ["-predicted_at", "-id"]
