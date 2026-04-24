from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.maintenance.filters import (
    CurativeTicketFilter,
    MaintenanceAssetFilter,
    PreventivePlanFilter,
    PreventiveScheduleFilter,
)
from apps.maintenance.models import (
    CurativeAction,
    CurativePart,
    CurativeTicket,
    MaintenanceAsset,
    PreventiveExecutionPart,
    PreventivePart,
    PreventivePlan,
    PreventiveSchedule,
    PreventiveTask,
)
from .serializers import (
    CurativeActionSerializer,
    CurativePartSerializer,
    CurativeTicketSerializer,
    MaintenanceAssetSerializer,
    PreventiveExecutionPartSerializer,
    PreventivePartSerializer,
    PreventivePlanSerializer,
    PreventiveScheduleSerializer,
    PreventiveTaskSerializer,
)



class MaintenanceAssetViewSet(ModelViewSet):
    queryset = MaintenanceAsset.objects.all()
    serializer_class = MaintenanceAssetSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = MaintenanceAssetFilter
    search_fields = ["asset_code", "asset_name", "tester_id", "location", "manufacturer", "model", "serial_number"]
    ordering_fields = ["asset_code", "asset_name", "created_at", "updated_at"]
    ordering = ["asset_code"]


class CurativeTicketViewSet(ModelViewSet):
    queryset = CurativeTicket.objects.select_related("asset", "source_alert_event", "assigned_to", "closed_by").all()
    serializer_class = CurativeTicketSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = CurativeTicketFilter
    search_fields = ["ticket_code", "title", "symptom", "failure_cause", "comment", "asset__asset_code", "asset__tester_id"]
    ordering_fields = ["opened_at", "closed_at", "created_at", "updated_at", "ticket_code"]
    ordering = ["-opened_at", "-id"]


class CurativeActionViewSet(ModelViewSet):
    queryset = CurativeAction.objects.select_related("ticket", "performed_by").all()
    serializer_class = CurativeActionSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["ticket__ticket_code", "diagnosis", "failure_cause", "action_taken", "comment"]
    ordering_fields = ["started_at", "ended_at", "created_at", "updated_at"]
    ordering = ["-started_at", "-id"]

    def perform_create(self, serializer):
        serializer.save(performed_by=self.request.user)


class CurativePartViewSet(ModelViewSet):
    queryset = CurativePart.objects.select_related("ticket", "part").all()
    serializer_class = CurativePartSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["ticket__ticket_code", "part__part_code", "part__designation", "comment"]
    ordering_fields = ["created_at", "planned_quantity", "consumed_quantity"]
    ordering = ["-created_at", "-id"]

class PreventivePlanViewSet(ModelViewSet):
    queryset = PreventivePlan.objects.select_related("asset").all()
    serializer_class = PreventivePlanSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = PreventivePlanFilter
    search_fields = ["plan_code", "plan_name", "asset__asset_code", "asset__tester_id"]
    ordering_fields = ["plan_code", "plan_name", "created_at", "updated_at"]
    ordering = ["plan_code"]


class PreventiveTaskViewSet(ModelViewSet):
    queryset = PreventiveTask.objects.select_related("plan").all()
    serializer_class = PreventiveTaskSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["plan__plan_code", "task_label", "instruction"]
    ordering_fields = ["step_order", "created_at"]
    ordering = ["plan", "step_order"]


class PreventivePartViewSet(ModelViewSet):
    queryset = PreventivePart.objects.select_related("plan", "part").all()
    serializer_class = PreventivePartSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["plan__plan_code", "part__part_code", "part__designation", "comment"]
    ordering_fields = ["created_at", "planned_quantity"]
    ordering = ["plan", "part__part_code"]


class PreventiveScheduleViewSet(ModelViewSet):
    queryset = PreventiveSchedule.objects.select_related("plan", "performed_by").all()
    serializer_class = PreventiveScheduleSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = PreventiveScheduleFilter
    search_fields = ["plan__plan_code", "plan__plan_name", "comment"]
    ordering_fields = ["scheduled_for", "performed_at", "created_at", "updated_at"]
    ordering = ["-scheduled_for", "-id"]


class PreventiveExecutionPartViewSet(ModelViewSet):
    queryset = PreventiveExecutionPart.objects.select_related("schedule", "part").all()
    serializer_class = PreventiveExecutionPartSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["schedule__plan__plan_code", "part__part_code", "part__designation", "comment"]
    ordering_fields = ["created_at", "planned_quantity", "consumed_quantity"]
    ordering = ["-created_at", "-id"]