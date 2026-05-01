from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.intelligence.api.views import (
    FailureEnrichmentViewSet,
    RepairHistoryViewSet,
    RepairPredictionViewSet,
    RepairProcedureTemplateViewSet,
)

router = DefaultRouter()
router.register(r"repair-history", RepairHistoryViewSet, basename="intelligence-repair-history")
router.register(r"repair-procedure-templates", RepairProcedureTemplateViewSet, basename="intelligence-repair-procedure-templates")
router.register(r"failure-enrichments", FailureEnrichmentViewSet, basename="intelligence-failure-enrichments")
router.register(r"enrichments", FailureEnrichmentViewSet, basename="intelligence-enrichments-legacy")
router.register(r"repair-predictions", RepairPredictionViewSet, basename="intelligence-repair-predictions")
router.register(r"predictions", RepairPredictionViewSet, basename="intelligence-predictions-legacy")

urlpatterns = [
    path("", include(router.urls)),
]
