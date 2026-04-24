import django_filters

from .models import Board


class BoardFilter(django_filters.FilterSet):
    serial_number = django_filters.CharFilter(field_name="serial_number", lookup_expr="icontains")
    client_reference = django_filters.CharFilter(field_name="client_reference", lookup_expr="icontains")
    internal_reference = django_filters.CharFilter(field_name="internal_reference", lookup_expr="icontains")
    current_status = django_filters.ChoiceFilter(field_name="current_status", choices=Board.Status.choices)

    first_seen_at_after = django_filters.DateTimeFilter(field_name="first_seen_at", lookup_expr="gte")
    first_seen_at_before = django_filters.DateTimeFilter(field_name="first_seen_at", lookup_expr="lte")
    last_seen_at_after = django_filters.DateTimeFilter(field_name="last_seen_at", lookup_expr="gte")
    last_seen_at_before = django_filters.DateTimeFilter(field_name="last_seen_at", lookup_expr="lte")

    class Meta:
        model = Board
        fields = [
            "serial_number",
            "client_reference",
            "internal_reference",
            "current_status",
        ]