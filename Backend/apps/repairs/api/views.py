from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.boards.models import Board
from apps.failures.models import FailureCase
from apps.repairs.filters import RepairActionFilter, RepairTicketFilter
from apps.repairs.models import RepairAction, RepairTicket
from apps.repairs.permission import RepairActionPermission
from apps.repairs import services as repair_services
from common.pagination import StandardResultsSetPagination

from .serializers import RepairActionSerializer, RepairTicketSerializer


class RepairTicketViewSet(ModelViewSet):
    queryset = RepairTicket.objects.select_related("failure_case", "failure_case__board").all()
    serializer_class = RepairTicketSerializer
    permission_classes = [RepairActionPermission]
    pagination_class = StandardResultsSetPagination
    filterset_class = RepairTicketFilter
    search_fields = [
        "ticket_code",
        "failure_case__serial_number",
        "failure_case__client_reference",
        "failure_case__internal_reference",
    ]
    ordering_fields = ["opened_at", "closed_at", "cycle_number", "ticket_code", "updated_at"]
    ordering = ["-opened_at", "-id"]

    def perform_create(self, serializer):
        ticket = serializer.save()
        failure_case = ticket.failure_case
        board = failure_case.board

        if failure_case.failure_status == FailureCase.Status.IN_DEFECT:
            failure_case.failure_status = FailureCase.Status.IN_REPAIR
            failure_case.save(update_fields=["failure_status", "updated_at"])

        if board.current_status in [Board.Status.HEALTHY, Board.Status.IN_DEFECT]:
            board.current_status = Board.Status.IN_REPAIR
            board.save(update_fields=["current_status", "updated_at"])

        repair_services.apply_repair_ticket_workflow(ticket)

    def perform_update(self, serializer):
        ticket = serializer.save()
        repair_services.apply_repair_ticket_workflow(ticket)


class RepairActionViewSet(ModelViewSet):
    queryset = RepairAction.objects.select_related(
        "repair_ticket",
        "repair_ticket__failure_case",
        "repair_ticket__failure_case__board",
        "technician",
    ).all()
    serializer_class = RepairActionSerializer
    permission_classes = [RepairActionPermission]
    pagination_class = StandardResultsSetPagination
    filterset_class = RepairActionFilter
    search_fields = [
        "repair_ticket__ticket_code",
        "repair_ticket__failure_case__serial_number",
        "defect_type",
        "observed_defect",
        "detected_cause",
        "action_taken",
        "technician__matricule",
    ]
    ordering_fields = ["performed_at", "created_at", "updated_at"]
    ordering = ["-performed_at", "-id"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        repair_action = (
            self.get_queryset()
            .get(pk=serializer.instance.pk)
        )
        response_serializer = self.get_serializer(repair_action)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        repair_action = serializer.save(technician=self.request.user)
        repair_services.apply_repair_workflow(repair_action)

    def perform_update(self, serializer):
        repair_action = serializer.save()
        repair_services.apply_repair_workflow(repair_action)
