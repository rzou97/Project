from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.calibration.api.views import CalibrationRecordViewSet, InstrumentViewSet

router = DefaultRouter()
router.register(r"instruments", InstrumentViewSet, basename="calibration-instruments")
router.register(r"records", CalibrationRecordViewSet, basename="calibration-records")

urlpatterns = [
    path("", include(router.urls)),
]