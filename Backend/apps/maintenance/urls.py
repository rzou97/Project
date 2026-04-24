from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.maintenance.api.views import (
    CurativeActionViewSet,
    CurativePartViewSet,
    CurativeTicketViewSet,
    MaintenanceAssetViewSet,
    PreventiveExecutionPartViewSet,
    PreventivePartViewSet,
    PreventivePlanViewSet,
    PreventiveScheduleViewSet,
    PreventiveTaskViewSet,
)

router = DefaultRouter()
router.register(r"assets", MaintenanceAssetViewSet, basename="maintenance-assets")
router.register(r"curative-tickets", CurativeTicketViewSet, basename="maintenance-curative-tickets")
router.register(r"curative-actions", CurativeActionViewSet, basename="maintenance-curative-actions")
router.register(r"curative-parts", CurativePartViewSet, basename="maintenance-curative-parts")
router.register(r"preventive-plans", PreventivePlanViewSet, basename="maintenance-preventive-plans")
router.register(r"preventive-tasks", PreventiveTaskViewSet, basename="maintenance-preventive-tasks")
router.register(r"preventive-parts", PreventivePartViewSet, basename="maintenance-preventive-parts")
router.register(r"preventive-schedules", PreventiveScheduleViewSet, basename="maintenance-preventive-schedules")
router.register(r"preventive-execution-parts", PreventiveExecutionPartViewSet, basename="maintenance-preventive-execution-parts")

urlpatterns = [
    path("", include(router.urls)),
]