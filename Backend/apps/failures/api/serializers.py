from rest_framework import serializers

from apps.failures.models import FailureCase


class FailureCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FailureCase
        fields = (
            "id",
            "board",
            "source_test_result",
            "serial_number",
            "client_reference",
            "internal_reference",
            "failure_status",
            "detected_in_phase",
            "detected_on_tester",
            "failure_type",
            "failure_message",
            "opened_at",
            "closed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields