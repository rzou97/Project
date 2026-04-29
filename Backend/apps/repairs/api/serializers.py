from rest_framework import serializers

from apps.repairs.models import RepairAction, RepairTicket

TICKET_STATUS_CANCELLED = getattr(RepairTicket.Status, "CANCELLED", "CANCELLED")


class RepairTicketSerializer(serializers.ModelSerializer):
    serial_number = serializers.CharField(source="failure_case.serial_number", read_only=True)
    client_reference = serializers.CharField(source="failure_case.client_reference", read_only=True)
    internal_reference = serializers.CharField(source="failure_case.internal_reference", read_only=True)
    failure_status = serializers.CharField(source="failure_case.failure_status", read_only=True)
    detected_in_phase = serializers.CharField(source="failure_case.detected_in_phase", read_only=True)
    detected_on_tester = serializers.CharField(source="failure_case.detected_on_tester", read_only=True)
    failure_type = serializers.CharField(source="failure_case.failure_type", read_only=True)
    failure_message = serializers.CharField(source="failure_case.failure_message", read_only=True)
    board_status = serializers.CharField(source="failure_case.board.current_status", read_only=True)

    class Meta:
        model = RepairTicket
        fields = (
            "id",
            "failure_case",
            "serial_number",
            "client_reference",
            "internal_reference",
            "failure_status",
            "detected_in_phase",
            "detected_on_tester",
            "failure_type",
            "failure_message",
            "board_status",
            "ticket_code",
            "ticket_status",
            "cycle_number",
            "opened_at",
            "closed_at",
            "repair_effectiveness",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
        extra_kwargs = {
            "ticket_code": {"required": False},
            "cycle_number": {"required": False},
            "opened_at": {"required": False},
        }

    def validate_cycle_number(self, value):
        if value < 1:
            raise serializers.ValidationError("cycle_number doit etre superieur ou egal a 1.")
        return value

    def create(self, validated_data):
        from django.db.models import Max
        from django.utils import timezone

        failure_case = validated_data["failure_case"]

        cycle_number = validated_data.get("cycle_number")
        if not cycle_number:
            max_cycle = (
                RepairTicket.objects.filter(failure_case=failure_case)
                .aggregate(max_cycle=Max("cycle_number"))
                .get("max_cycle")
                or 0
            )
            cycle_number = max_cycle + 1
            validated_data["cycle_number"] = cycle_number

        if not validated_data.get("ticket_code"):
            serial = (failure_case.serial_number or "UNKNOWN").replace(" ", "")
            validated_data["ticket_code"] = f"RT-{serial}-{failure_case.id}-{cycle_number:03d}"

        if not validated_data.get("opened_at"):
            validated_data["opened_at"] = timezone.now()

        return super().create(validated_data)


class RepairActionSerializer(serializers.ModelSerializer):
    ticket_code = serializers.CharField(source="repair_ticket.ticket_code", read_only=True)
    technician_matricule = serializers.CharField(source="technician.matricule", read_only=True)
    serial_number = serializers.CharField(source="repair_ticket.failure_case.serial_number", read_only=True)
    client_reference = serializers.CharField(source="repair_ticket.failure_case.client_reference", read_only=True)
    internal_reference = serializers.CharField(source="repair_ticket.failure_case.internal_reference", read_only=True)
    failure_status = serializers.CharField(source="repair_ticket.failure_case.failure_status", read_only=True)
    failure_message = serializers.CharField(source="repair_ticket.failure_case.failure_message", read_only=True)
    ticket_status = serializers.CharField(source="repair_ticket.ticket_status", read_only=True)

    class Meta:
        model = RepairAction
        fields = (
            "id",
            "repair_ticket",
            "ticket_code",
            "serial_number",
            "client_reference",
            "internal_reference",
            "failure_status",
            "failure_message",
            "ticket_status",
            "technician",
            "technician_matricule",
            "defect_type",
            "observed_defect",
            "detected_cause",
            "action_taken",
            "action_progress",
            "performed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "technician",
            "technician_matricule",
            "ticket_code",
            "serial_number",
        )

    def validate(self, attrs):
        repair_ticket = attrs.get("repair_ticket")
        if not repair_ticket and self.instance:
            repair_ticket = self.instance.repair_ticket

        if repair_ticket and repair_ticket.ticket_status in [
            RepairTicket.Status.CLOSED,
            TICKET_STATUS_CANCELLED,
        ]:
            raise serializers.ValidationError(
                {
                    "repair_ticket": (
                        "Impossible d'ajouter/modifier une action sur un ticket ferme ou annule."
                    )
                }
            )

        if repair_ticket and "defect_type" in attrs and not attrs.get("defect_type"):
            attrs["defect_type"] = repair_ticket.failure_case.failure_type

        return attrs
