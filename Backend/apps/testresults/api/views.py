from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.testresults.filters import TestResultFilter
from apps.testresults.models import TestResult
from .serializers import TestResultSerializer


class TestResultViewSet(ReadOnlyModelViewSet):
    queryset = TestResult.objects.select_related("board").all()
    serializer_class = TestResultSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TestResultFilter
    search_fields = [
        "serial_number",
        "client_reference",
        "internal_reference",
        "tester_id",
        "failure_type",
        "failure_message",
        "operator_name",
        "source_event_key",
    ]
    ordering_fields = [
        "tested_at",
        "created_at",
        "updated_at",
        "serial_number",
        "client_reference",
        "internal_reference",
        "source_event_key",
    ]
    ordering = ["-tested_at", "-id"]