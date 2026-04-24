import django_filters

from .models import FailureCase


class FailureCaseFilter(django_filters.FilterSet):
    serial_number = django_filters.CharFilter(field_name="serial_number", lookup_expr="icontains")
    client_reference = django_filters.CharFilter(field_name="client_reference", lookup_expr="icontains")
    internal_reference = django_filters.CharFilter(field_name="internal_reference", lookup_expr="icontains")
    failure_status = django_filters.ChoiceFilter(field_name="failure_status", choices=FailureCase.Status.choices)
    detected_in_phase = django_filters.CharFilter(field_name="detected_in_phase", lookup_expr="exact")
    detected_on_tester = django_filters.CharFilter(field_name="detected_on_tester", lookup_expr="icontains")
    failure_type = django_filters.CharFilter(field_name="failure_type", lookup_expr="icontains")

    opened_at_after = django_filters.DateTimeFilter(field_name="opened_at", lookup_expr="gte")
    opened_at_before = django_filters.DateTimeFilter(field_name="opened_at", lookup_expr="lte")
    closed_at_after = django_filters.DateTimeFilter(field_name="closed_at", lookup_expr="gte")
    closed_at_before = django_filters.DateTimeFilter(field_name="closed_at", lookup_expr="lte")

    class Meta:
        model = FailureCase
        fields = [
            "serial_number",
            "client_reference",
            "internal_reference",
            "failure_status",
            "detected_in_phase",
            "detected_on_tester",
            "failure_type",
        ]