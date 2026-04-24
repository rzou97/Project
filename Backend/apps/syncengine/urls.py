from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.syncengine.api.views import (
    SyncCursorViewSet,
    SyncRunNowView,
    SyncTaskStatusView,
)

router = DefaultRouter()
router.register(r"cursors", SyncCursorViewSet, basename="syncengine-cursors")

urlpatterns = [
    path("", include(router.urls)),
    path("run/", SyncRunNowView.as_view(), name="syncengine-run"),
    path("tasks/<str:task_id>/", SyncTaskStatusView.as_view(), name="syncengine-task-status"),
]
