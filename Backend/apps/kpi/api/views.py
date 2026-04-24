from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.kpi.api.serializers import (
    TesterCurrentStatusKpiSerializer,
    TesterFpyInstantKpiSerializer,
)
from apps.kpi.services import KpiService


class TestersFpyInstantView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = KpiService.get_testers_fpy_instant()
        serializer = TesterFpyInstantKpiSerializer(data, many=True)
        return Response(serializer.data)


class TestersCurrentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = KpiService.get_testers_current_status()
        serializer = TesterCurrentStatusKpiSerializer(data, many=True)
        return Response(serializer.data)
