from rest_framework import serializers

from apps.alerts.models import AlertEvent, AlertRule


class AlertRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertRule
        fields = (
            "id",
            "name",
            "alert_type",
            "threshold_value",
            "time_window_minutes",
            "consecutive_count",
            "severity",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class AlertEventSerializer(serializers.ModelSerializer):
    rule_name = serializers.CharField(source="rule.name", read_only=True)
    asset_code = serializers.CharField(source="asset.asset_code", read_only=True)
    tester_id = serializers.CharField(source="asset.tester_id", read_only=True)

    class Meta:
        model = AlertEvent
        fields = (
            "id",
            "rule",
            "rule_name",
            "asset",
            "asset_code",
            "tester_id",
            "title",
            "description",
            "severity",
            "status",
            "entity_type",
            "entity_key",
            "triggered_at",
            "resolved_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")