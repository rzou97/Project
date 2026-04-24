import django_filters

from apps.alerts.models import AlertEvent, AlertRule


class AlertRuleFilter(django_filters.FilterSet):
    alert_type = django_filters.ChoiceFilter(field_name="alert_type", choices=AlertRule.AlertType.choices)
    severity = django_filters.ChoiceFilter(field_name="severity", choices=AlertRule.Severity.choices)
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = AlertRule
        fields = ["alert_type", "severity", "is_active"]


class AlertEventFilter(django_filters.FilterSet):
    rule = django_filters.NumberFilter(field_name="rule_id")
    asset = django_filters.NumberFilter(field_name="asset_id")
    severity = django_filters.ChoiceFilter(field_name="severity", choices=AlertRule.Severity.choices)
    status = django_filters.ChoiceFilter(field_name="status", choices=AlertEvent.Status.choices)
    triggered_at_after = django_filters.DateTimeFilter(field_name="triggered_at", lookup_expr="gte")
    triggered_at_before = django_filters.DateTimeFilter(field_name="triggered_at", lookup_expr="lte")

    class Meta:
        model = AlertEvent
        fields = ["rule", "asset", "severity", "status"]