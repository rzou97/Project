from rest_framework import serializers

from apps.intelligence.models import RepairHistory, RepairPrediction, RepairProcedureTemplate


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


class RepairPredictionSerializer(serializers.ModelSerializer):
    recommended_procedure_name = serializers.CharField(
        source="recommended_procedure.procedure_name",
        read_only=True,
    )

    class Meta:
        model = RepairPrediction
        fields = (
            "id",
            "prediction_type",
            "target_serial_number",
            "predicted_cause",
            "recommended_action",
            "recommended_procedure",
            "recommended_procedure_name",
            "confidence_score",
            "predicted_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "recommended_procedure_name")
