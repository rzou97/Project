from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.repairs.api.views import RepairActionViewSet, RepairTicketViewSet

router = DefaultRouter()
router.register(r"tickets", RepairTicketViewSet, basename="repair-tickets")
router.register(r"actions", RepairActionViewSet, basename="repair-actions")

urlpatterns = [
    path("", include(router.urls)),
]
