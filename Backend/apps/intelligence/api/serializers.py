from rest_framework import serializers

from apps.failures.models import FailureCase
from apps.repairs.models import RepairTicket
from apps.intelligence.models import (
    FailureEnrichment,
    RepairHistory,
    RepairPrediction,
    RepairProcedureTemplate,
)


class RepairHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairHistory
        fields = "__all__"
        read_only_fields = ("id", "created_at")


class RepairProcedureTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairProcedureTemplate
        fields = "__all__"
        read_only_fields = ("id",)


class FailureEnrichmentSerializer(serializers.ModelSerializer):
    serial_number = serializers.CharField(source="failure_case.serial_number", read_only=True)
    client_reference = serializers.CharField(source="failure_case.client_reference", read_only=True)
    internal_reference = serializers.CharField(source="failure_case.internal_reference", read_only=True)
    failure_type = serializers.CharField(source="failure_case.failure_type", read_only=True)
    failure_message = serializers.CharField(source="failure_case.failure_message", read_only=True)
    failure_status = serializers.CharField(source="failure_case.failure_status", read_only=True)

    class Meta:
        model = FailureEnrichment
        fields = (
            "id",
            "failure_case",
            "serial_number",
            "client_reference",
            "internal_reference",
            "failure_type",
            "failure_message",
            "failure_status",
            "normalized_family",
            "normalized_signature",
            "probable_root_cause",
            "suggested_action",
            "suggested_checks",
            "suspect_components",
            "supporting_history_count",
            "confidence_score",
            "needs_human_review",
            "enrichment_source",
            "model_name",
            "model_version",
            "prompt_version",
            "evidence_json",
            "enriched_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class FailureAnalysisRequestSerializer(serializers.Serializer):
    failure_case = serializers.PrimaryKeyRelatedField(queryset=FailureCase.objects.all())
    repair_ticket = serializers.PrimaryKeyRelatedField(
        queryset=RepairTicket.objects.all(),
        required=False,
        allow_null=True,
    )

    def validate(self, attrs):
        failure_case = attrs["failure_case"]
        repair_ticket = attrs.get("repair_ticket")

        if repair_ticket and repair_ticket.failure_case_id != failure_case.id:
            raise serializers.ValidationError(
                {"repair_ticket": "Le ticket doit etre lie a la meme panne."}
            )

        return attrs


class RepairPredictionSerializer(serializers.ModelSerializer):
    recommended_procedure_name = serializers.CharField(
        source="recommended_procedure.procedure_name",
        read_only=True,
    )

    class Meta:
        model = RepairPrediction
        fields = (
            "id",
            "failure_case",
            "repair_ticket",
            "prediction_type",
            "target_serial_number",
            "predicted_cause",
            "recommended_action",
            "recommended_procedure",
            "recommended_procedure_name",
            "prediction_source",
            "model_name",
            "model_version",
            "input_signature",
            "explanation_json",
            "confidence_score",
            "predicted_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "recommended_procedure_name")


class FailureAnalysisResponseSerializer(serializers.Serializer):
    enrichment = FailureEnrichmentSerializer()
    prediction = RepairPredictionSerializer()
