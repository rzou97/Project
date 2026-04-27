from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.failures.filters import FailureCaseFilter
from apps.failures.models import FailureCase
from common.pagination import StandardResultsSetPagination
from .serializers import FailureCaseSerializer


class FailureCaseViewSet(ReadOnlyModelViewSet):
    queryset = FailureCase.objects.select_related("board", "source_test_result").all()
    serializer_class = FailureCaseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filterset_class = FailureCaseFilter
    search_fields = [
        "serial_number",
        "client_reference",
        "internal_reference",
        "failure_type",
        "failure_message",
        "detected_on_tester",
    ]
    ordering_fields = [
        "opened_at",
        "closed_at",
        "created_at",
        "updated_at",
        "serial_number",
        "client_reference",
        "internal_reference",
    ]
    ordering = ["-opened_at", "-id"]
