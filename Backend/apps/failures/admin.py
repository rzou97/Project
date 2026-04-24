from django.contrib import admin

from .models import FailureCase


@admin.register(FailureCase)
class FailureCaseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "serial_number",
        "client_reference",
        "internal_reference",
        "failure_status",
        "detected_in_phase",
        "detected_on_tester",
        "failure_type",
        "opened_at",
        "closed_at",
    )
    list_filter = (
        "failure_status",
        "detected_in_phase",
        "detected_on_tester",
        "client_reference",
        "internal_reference",
    )
    search_fields = (
        "serial_number",
        "client_reference",
        "internal_reference",
        "failure_type",
        "failure_message",
        "detected_on_tester",
    )
    ordering = ("-opened_at", "-id")