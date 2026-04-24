from rest_framework import serializers


class TesterFpyInstantKpi(serializers.Serializer):
    tester_id = serializers.CharField()
    day_date = serializers.DateField()
    unique_sn_tested = serializers.IntegerField()
    unique_sn_passed = serializers.IntegerField()
    fpy_instant = serializers.DecimalField(max_digits=8, decimal_places=2)
    last_test_at = serializers.DateTimeField(allow_null=True)


class TesterCurrentStatusKpi(serializers.Serializer):
    tester_id = serializers.CharField()
    operator_name = serializers.CharField(allow_blank=True)
    internal_reference = serializers.CharField(allow_blank=True)
    last_test_at = serializers.DateTimeField(allow_null=True)
    current_fail_rate = serializers.DecimalField(max_digits=8, decimal_places=2)
    current_status = serializers.CharField()
    alert_status = serializers.CharField()
    open_alert_count = serializers.IntegerField()
    open_alert_types = serializers.ListField(child=serializers.CharField())
    total_tests_current_hour = serializers.IntegerField()
    failed_tests_current_hour = serializers.IntegerField()


# Backward-compatible serializer names used by existing imports.
class TesterFpyInstantKpiSerializer(TesterFpyInstantKpi):
    pass


class TesterCurrentStatusKpiSerializer(TesterCurrentStatusKpi):
    pass


class TesterFpyInstantSerializer(TesterFpyInstantKpi):
    pass


class TesterCurrentStatusSerializer(TesterCurrentStatusKpi):
    pass
