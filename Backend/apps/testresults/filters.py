import django_filters

from .models import TestResult


class TestResultFilter(django_filters.FilterSet):
    serial_number = django_filters.CharFilter(field_name="serial_number", lookup_expr="icontains")
    client_reference = django_filters.CharFilter(field_name="client_reference", lookup_expr="icontains")
    internal_reference = django_filters.CharFilter(field_name="internal_reference", lookup_expr="icontains")
    test_phase = django_filters.ChoiceFilter(field_name="test_phase", choices=TestResult.Phase.choices)
    tester_id = django_filters.CharFilter(field_name="tester_id", lookup_expr="icontains")
    result = django_filters.ChoiceFilter(field_name="result", choices=TestResult.Result.choices)
    failure_type = django_filters.CharFilter(field_name="failure_type", lookup_expr="icontains")
    operator_name = django_filters.CharFilter(field_name="operator_name", lookup_expr="icontains")

    tested_at_after = django_filters.DateTimeFilter(field_name="tested_at", lookup_expr="gte")
    tested_at_before = django_filters.DateTimeFilter(field_name="tested_at", lookup_expr="lte")

    class Meta:
        model = TestResult
        fields = [
            "serial_number",
            "client_reference",
            "internal_reference",
            "test_phase",
            "tester_id",
            "result",
            "failure_type",
            "operator_name",
        ]