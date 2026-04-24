from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.testresults.api.views import TestResultViewSet

router = DefaultRouter()
router.register(r"", TestResultViewSet, basename="test-results")

urlpatterns = [
    path("", include(router.urls)),
]