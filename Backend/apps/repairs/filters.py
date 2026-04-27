import django_filters

from apps.repairs.models import RepairAction, RepairTicket


class RepairTicketFilter(django_filters.FilterSet):
    failure_case = django_filters.NumberFilter(field_name="failure_case_id")
    serial_number = django_filters.CharFilter(
        field_name="failure_case__serial_number",
        lookup_expr="icontains",
    )
    client_reference = django_filters.CharFilter(
        field_name="failure_case__client_reference",
        lookup_expr="icontains",
    )
    internal_reference = django_filters.CharFilter(
        field_name="failure_case__internal_reference",
        lookup_expr="icontains",
    )
    ticket_code = django_filters.CharFilter(field_name="ticket_code", lookup_expr="icontains")
    ticket_status = django_filters.ChoiceFilter(field_name="ticket_status", choices=RepairTicket.Status.choices)
    cycle_number = django_filters.NumberFilter(field_name="cycle_number")
    opened_at_after = django_filters.DateTimeFilter(field_name="opened_at", lookup_expr="gte")
    opened_at_before = django_filters.DateTimeFilter(field_name="opened_at", lookup_expr="lte")

    class Meta:
        model = RepairTicket
        fields = [
            "failure_case",
            "serial_number",
            "client_reference",
            "internal_reference",
            "ticket_code",
            "ticket_status",
            "cycle_number",
        ]


class RepairActionFilter(django_filters.FilterSet):
    repair_ticket = django_filters.NumberFilter(field_name="repair_ticket_id")
    ticket_code = django_filters.CharFilter(field_name="repair_ticket__ticket_code", lookup_expr="icontains")
    serial_number = django_filters.CharFilter(
        field_name="repair_ticket__failure_case__serial_number",
        lookup_expr="icontains",
    )
    client_reference = django_filters.CharFilter(
        field_name="repair_ticket__failure_case__client_reference",
        lookup_expr="icontains",
    )
    internal_reference = django_filters.CharFilter(
        field_name="repair_ticket__failure_case__internal_reference",
        lookup_expr="icontains",
    )
    action_progress = django_filters.ChoiceFilter(field_name="action_progress", choices=RepairAction.Progress.choices)
    defect_type = django_filters.CharFilter(field_name="defect_type", lookup_expr="icontains")
    technician = django_filters.NumberFilter(field_name="technician_id")
    performed_at_after = django_filters.DateTimeFilter(field_name="performed_at", lookup_expr="gte")
    performed_at_before = django_filters.DateTimeFilter(field_name="performed_at", lookup_expr="lte")

    class Meta:
        model = RepairAction
        fields = [
            "repair_ticket",
            "ticket_code",
            "serial_number",
            "client_reference",
            "internal_reference",
            "action_progress",
            "defect_type",
            "technician",
        ]
