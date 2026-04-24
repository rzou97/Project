from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from apps.alerts.filters import AlertEventFilter, AlertRuleFilter
from apps.alerts.models import AlertEvent, AlertRule
from .serializers import AlertEventSerializer, AlertRuleSerializer


class AlertRuleViewSet(ModelViewSet):
    queryset = AlertRule.objects.all()
    serializer_class = AlertRuleSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = AlertRuleFilter
    search_fields = ["name"]
    ordering_fields = ["name", "created_at", "updated_at"]
    ordering = ["name"]


class AlertEventViewSet(ReadOnlyModelViewSet):
    queryset = AlertEvent.objects.select_related("rule", "asset").all()
    serializer_class = AlertEventSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = AlertEventFilter
    search_fields = ["title", "description", "entity_key", "asset__asset_code", "asset__tester_id"]
    ordering_fields = ["triggered_at", "resolved_at", "created_at", "updated_at"]
    ordering = ["-triggered_at", "-id"]