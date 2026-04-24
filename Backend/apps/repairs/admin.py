from django.contrib import admin

from apps.repairs.models import RepairAction, RepairTicket


@admin.register(RepairTicket)
class RepairTicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "ticket_code",
        "failure_case",
        "ticket_status",
        "cycle_number",
        "opened_at",
        "closed_at",
        "repair_effectiveness",
    )
    list_filter = ("ticket_status", "cycle_number")
    search_fields = ("ticket_code", "failure_case__serial_number")
    ordering = ("-opened_at", "-id")


@admin.register(RepairAction)
class RepairActionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "repair_ticket",
        "technician",
        "defect_type",
        "action_progress",
        "performed_at",
        "created_at",
    )
    list_filter = ("action_progress", "defect_type", "technician")
    search_fields = (
        "repair_ticket__ticket_code",
        "repair_ticket__failure_case__serial_number",
        "defect_type",
        "observed_defect",
        "detected_cause",
        "action_taken",
        "technician__email",
        "technician__matricule",
    )
    ordering = ("-performed_at", "-id")
