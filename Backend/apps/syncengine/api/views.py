from celery.result import AsyncResult
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.syncengine.models import SyncCursor
from apps.syncengine.tasks import sync_enriched_events_task
from config.celery import app as celery_app

from .serializers import (
    SyncCursorSerializer,
    SyncRunRequestSerializer,
    SyncRunResponseSerializer,
    SyncTaskStatusSerializer,
)


def _serialize_task_result(value):
    if isinstance(value, (dict, list, str, int, float, bool)) or value is None:
        return value
    return str(value)


class SyncCursorViewSet(ReadOnlyModelViewSet):
    queryset = SyncCursor.objects.all()
    serializer_class = SyncCursorSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["source_table", "sync_status"]
    search_fields = ["source_table", "error_message"]
    ordering_fields = [
        "source_table",
        "sync_status",
        "last_synced_at",
        "last_source_timestamp",
        "updated_at",
        "rows_processed",
    ]
    ordering = ["source_table"]


class SyncRunNowView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=SyncRunRequestSerializer,
        responses={202: SyncRunResponseSerializer},
    )
    def post(self, request):
        serializer = SyncRunRequestSerializer(data=request.data or {})
        serializer.is_valid(raise_exception=True)

        limit = serializer.validated_data["limit"]
        async_result = sync_enriched_events_task.delay(limit=limit)

        payload = {
            "task_id": async_result.id,
            "state": async_result.state,
            "queued_at": timezone.now(),
            "limit": limit,
        }
        return Response(payload, status=status.HTTP_202_ACCEPTED)


class SyncTaskStatusView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: SyncTaskStatusSerializer})
    def get(self, request, task_id):
        async_result = AsyncResult(task_id, app=celery_app)

        payload = {
            "task_id": task_id,
            "state": async_result.state,
            "ready": async_result.ready(),
            "successful": async_result.successful(),
            "failed": async_result.failed(),
        }

        if async_result.successful():
            payload["result"] = _serialize_task_result(async_result.result)
        elif async_result.failed():
            payload["error"] = str(async_result.result)

        return Response(payload, status=status.HTTP_200_OK)
