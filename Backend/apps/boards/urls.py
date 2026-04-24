from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.boards.api.views import BoardViewSet

router = DefaultRouter()
router.register(r"", BoardViewSet, basename="boards")

urlpatterns = [
    path("", include(router.urls)),
]