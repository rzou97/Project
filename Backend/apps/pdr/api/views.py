from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from apps.pdr.filters import PartFilter, PartStockMovementFilter
from apps.pdr.models import Part, PartStock, PartStockMovement
from .serializers import PartSerializer, PartStockMovementSerializer, PartStockSerializer


class PartViewSet(ModelViewSet):
    queryset = Part.objects.all()
    serializer_class = PartSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = PartFilter
    search_fields = ["part_code", "designation", "manufacturer", "affectation_value"]
    ordering_fields = ["part_code", "designation", "created_at", "updated_at"]
    ordering = ["part_code"]


class PartStockViewSet(ReadOnlyModelViewSet):
    queryset = PartStock.objects.select_related("part").all()
    serializer_class = PartStockSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["part__part_code", "part__designation"]
    ordering_fields = ["current_quantity", "reserved_quantity", "updated_at"]
    ordering = ["part__part_code"]


class PartStockMovementViewSet(ModelViewSet):
    queryset = PartStockMovement.objects.select_related("part", "performed_by").all()
    serializer_class = PartStockMovementSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = PartStockMovementFilter
    search_fields = ["part__part_code", "part__designation", "source_reference", "comment"]
    ordering_fields = ["performed_at", "created_at", "quantity"]
    ordering = ["-performed_at", "-id"]

    def perform_create(self, serializer):
        serializer.save(performed_by=self.request.user)