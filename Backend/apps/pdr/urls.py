from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.pdr.api.views import PartStockMovementViewSet, PartStockViewSet, PartViewSet

router = DefaultRouter()
router.register(r"parts", PartViewSet, basename="pdr-parts")
router.register(r"stocks", PartStockViewSet, basename="pdr-stocks")
router.register(r"movements", PartStockMovementViewSet, basename="pdr-movements")

urlpatterns = [
    path("", include(router.urls)),
]