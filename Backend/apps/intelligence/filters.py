import django_filters

from apps.intelligence.models import RepairHistory, RepairPrediction, RepairProcedureTemplate


class RepairHistoryFilter(django_filters.FilterSet):
    serial_number = django_filters.CharFilter(field_name="serial_number", lookup_expr="icontains")
    client_reference = django_filters.CharFilter(field_name="client_reference", lookup_expr="icontains")
    internal_reference = django_filters.CharFilter(field_name="internal_reference", lookup_expr="icontains")
    failure_type = django_filters.CharFilter(field_name="failure_type", lookup_expr="icontains")
    detected_in_phase = django_filters.CharFilter(field_name="detected_in_phase", lookup_expr="exact")
    detected_on_tester = django_filters.CharFilter(field_name="detected_on_tester", lookup_expr="icontains")
    technician_matricule = django_filters.CharFilter(field_name="technician_matricule", lookup_expr="icontains")
    final_outcome = django_filters.CharFilter(field_name="final_outcome", lookup_expr="iexact")
    repair_cycle_count = django_filters.NumberFilter(field_name="repair_cycle_count")
    created_at_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_at_before = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = RepairHistory
        fields = [
            "serial_number",
            "client_reference",
            "internal_reference",
            "failure_type",
            "detected_in_phase",
            "detected_on_tester",
            "technician_matricule",
            "final_outcome",
            "repair_cycle_count",
        ]


class RepairProcedureTemplateFilter(django_filters.FilterSet):
    procedure_name = django_filters.CharFilter(field_name="procedure_name", lookup_expr="icontains")
    failure_type = django_filters.CharFilter(field_name="failure_type", lookup_expr="icontains")
    failure_signature = django_filters.CharFilter(field_name="failure_signature", lookup_expr="icontains")
    version = django_filters.CharFilter(field_name="version", lookup_expr="iexact")
    generated_at_after = django_filters.DateTimeFilter(field_name="generated_at", lookup_expr="gte")
    generated_at_before = django_filters.DateTimeFilter(field_name="generated_at", lookup_expr="lte")

    class Meta:
        model = RepairProcedureTemplate
        fields = ["procedure_name", "failure_type", "failure_signature", "version"]


class RepairPredictionFilter(django_filters.FilterSet):
    prediction_type = django_filters.CharFilter(field_name="prediction_type", lookup_expr="iexact")
    target_serial_number = django_filters.CharFilter(field_name="target_serial_number", lookup_expr="icontains")
    predicted_at_after = django_filters.DateTimeFilter(field_name="predicted_at", lookup_expr="gte")
    predicted_at_before = django_filters.DateTimeFilter(field_name="predicted_at", lookup_expr="lte")

    class Meta:
        model = RepairPrediction
        fields = ["prediction_type", "target_serial_number"]
