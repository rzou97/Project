from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.failures.api.views import FailureCaseViewSet

router = DefaultRouter()
router.register(r"", FailureCaseViewSet, basename="failure-cases")

urlpatterns = [
    path("", include(router.urls)),
]