from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.alerts.api.views import AlertEventViewSet, AlertRuleViewSet

router = DefaultRouter()
router.register(r"rules", AlertRuleViewSet, basename="alert-rules")
router.register(r"events", AlertEventViewSet, basename="alert-events")

urlpatterns = [
    path("", include(router.urls)),
]