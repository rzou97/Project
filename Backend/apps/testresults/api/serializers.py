from rest_framework import serializers

from apps.testresults.models import TestResult


class TestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResult
        fields = (
            "id",
            "board",
            "serial_number",
            "client_reference",
            "internal_reference",
            "operator_name",
            "tester_id",
            "test_phase",
            "result",
            "failure_type",
            "failure_message",
            "tested_at",
            "source_event_key",
            "raw_ingested_ts",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields