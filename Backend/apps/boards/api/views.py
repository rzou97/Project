from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.boards.filters import BoardFilter
from apps.boards.models import Board
from .serializers import BoardSerializer


class BoardViewSet(ReadOnlyModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = BoardFilter
    search_fields = ["serial_number", "client_reference", "internal_reference"]
    ordering_fields = [
        "created_at",
        "updated_at",
        "first_seen_at",
        "last_seen_at",
        "serial_number",
        "client_reference",
        "internal_reference",
    ]
    ordering = ["-updated_at"]