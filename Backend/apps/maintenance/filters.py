import django_filters

from apps.maintenance.models import (
CurativeTicket, 
MaintenanceAsset,
PreventivePlan,
PreventiveSchedule,
)


class MaintenanceAssetFilter(django_filters.FilterSet):
    asset_code = django_filters.CharFilter(field_name="asset_code", lookup_expr="icontains")
    asset_name = django_filters.CharFilter(field_name="asset_name", lookup_expr="icontains")
    asset_type = django_filters.ChoiceFilter(field_name="asset_type", choices=MaintenanceAsset.AssetType.choices)
    tester_id = django_filters.CharFilter(field_name="tester_id", lookup_expr="icontains")
    status = django_filters.ChoiceFilter(field_name="status", choices=MaintenanceAsset.Status.choices)
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = MaintenanceAsset
        fields = ["asset_code", "asset_name", "asset_type", "tester_id", "status", "is_active"]


class CurativeTicketFilter(django_filters.FilterSet):
    asset = django_filters.NumberFilter(field_name="asset_id")
    trigger_type = django_filters.ChoiceFilter(field_name="trigger_type", choices=CurativeTicket.TriggerType.choices)
    status = django_filters.ChoiceFilter(field_name="status", choices=CurativeTicket.Status.choices)
    opened_at_after = django_filters.DateTimeFilter(field_name="opened_at", lookup_expr="gte")
    opened_at_before = django_filters.DateTimeFilter(field_name="opened_at", lookup_expr="lte")

    class Meta:
        model = CurativeTicket
        fields = ["asset", "trigger_type", "status"]

class PreventivePlanFilter(django_filters.FilterSet):
    asset = django_filters.NumberFilter(field_name="asset_id")
    frequency = django_filters.ChoiceFilter(field_name="frequency", choices=PreventivePlan.Frequency.choices)
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = PreventivePlan
        fields = ["asset", "frequency", "is_active"]


class PreventiveScheduleFilter(django_filters.FilterSet):
    plan = django_filters.NumberFilter(field_name="plan_id")
    status = django_filters.ChoiceFilter(field_name="status", choices=PreventiveSchedule.Status.choices)
    scheduled_for_after = django_filters.DateTimeFilter(field_name="scheduled_for", lookup_expr="gte")
    scheduled_for_before = django_filters.DateTimeFilter(field_name="scheduled_for", lookup_expr="lte")

    class Meta:
        model = PreventiveSchedule
        fields = ["plan", "status"]