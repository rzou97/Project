from rest_framework import serializers

from apps.boards.models import Board


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = (
            "id",
            "serial_number",
            "client_reference",
            "internal_reference",
            "current_status",
            "first_seen_at",
            "last_seen_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_serial_number(self, value):
        return value.strip().upper()

    def validate_client_reference(self, value):
        return value.strip().upper()

    def validate_internal_reference(self, value):
        return value.strip().upper()

    def validate(self, attrs):
        first_seen_at = attrs.get("first_seen_at")
        last_seen_at = attrs.get("last_seen_at")

        if self.instance:
            first_seen_at = first_seen_at or self.instance.first_seen_at
            last_seen_at = last_seen_at or self.instance.last_seen_at

        if first_seen_at and last_seen_at and last_seen_at < first_seen_at:
            raise serializers.ValidationError(
                {"last_seen_at": "last_seen_at doit être supérieur ou égal à first_seen_at."}
            )

        return attrs