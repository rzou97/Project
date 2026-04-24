from rest_framework import serializers

from apps.maintenance.models import (
    CurativeAction,
    CurativePart,
    CurativeTicket,
    MaintenanceAsset,
    PreventiveExecutionPart,
    PreventivePart,
    PreventivePlan,
    PreventiveSchedule,
    PreventiveTask,
)


class MaintenanceAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceAsset
        fields = (
            "id",
            "asset_code",
            "asset_name",
            "asset_type",
            "tester_id",
            "location",
            "status",
            "manufacturer",
            "model",
            "serial_number",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class CurativeTicketSerializer(serializers.ModelSerializer):
    assigned_to_matricule = serializers.CharField(source="assigned_to.matricule", read_only=True)

    class Meta:
        model = CurativeTicket
        fields = (
            "id",
            "asset",
            "source_alert_event",
            "ticket_code",
            "trigger_type",
            "title",
            "symptom",
            "failure_cause",
            "comment",
            "downtime_start",
            "downtime_end",
            "downtime_minutes",
            "status",
            "opened_by_system",
            "assigned_to",
            "assigned_to_matricule",
            "closed_by",
            "opened_at",
            "closed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "assigned_to_matricule")


class CurativeActionSerializer(serializers.ModelSerializer):
    performer_matricule = serializers.CharField(source="performed_by.matricule", read_only=True)

    class Meta:
        model = CurativeAction
        fields = (
            "id",
            "ticket",
            "performed_by",
            "performer_matricule",
            "diagnosis",
            "failure_cause",
            "action_taken",
            "comment",
            "started_at",
            "ended_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "performed_by", "performer_matricule")


class CurativePartSerializer(serializers.ModelSerializer):
    part_code = serializers.CharField(source="part.part_code", read_only=True)
    part_designation = serializers.CharField(source="part.designation", read_only=True)

    class Meta:
        model = CurativePart
        fields = (
            "id",
            "ticket",
            "part",
            "part_code",
            "part_designation",
            "planned_quantity",
            "consumed_quantity",
            "comment",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "part_code", "part_designation")

class PreventivePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreventivePlan
        fields = (
            "id",
            "asset",
            "plan_code",
            "plan_name",
            "frequency",
            "description",
            "estimated_duration_minutes",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class PreventiveTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreventiveTask
        fields = (
            "id",
            "plan",
            "step_order",
            "task_label",
            "instruction",
            "is_mandatory",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class PreventivePartSerializer(serializers.ModelSerializer):
    part_code = serializers.CharField(source="part.part_code", read_only=True)
    part_designation = serializers.CharField(source="part.designation", read_only=True)

    class Meta:
        model = PreventivePart
        fields = (
            "id",
            "plan",
            "part",
            "part_code",
            "part_designation",
            "planned_quantity",
            "comment",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "part_code", "part_designation")


class PreventiveScheduleSerializer(serializers.ModelSerializer):
    performer_matricule = serializers.CharField(source="performed_by.matricule", read_only=True)

    class Meta:
        model = PreventiveSchedule
        fields = (
            "id",
            "plan",
            "scheduled_for",
            "status",
            "performed_by",
            "performer_matricule",
            "performed_at",
            "comment",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "performer_matricule")


class PreventiveExecutionPartSerializer(serializers.ModelSerializer):
    part_code = serializers.CharField(source="part.part_code", read_only=True)
    part_designation = serializers.CharField(source="part.designation", read_only=True)

    class Meta:
        model = PreventiveExecutionPart
        fields = (
            "id",
            "schedule",
            "part",
            "part_code",
            "part_designation",
            "planned_quantity",
            "consumed_quantity",
            "comment",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "part_code", "part_designation")