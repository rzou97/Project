from django.contrib import admin

from .models import TestResult


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "serial_number",
        "client_reference",
        "internal_reference",
        "test_phase",
        "tester_id",
        "result",
        "tested_at",
        "source_event_key",
    )
    list_filter = (
        "test_phase",
        "result",
        "client_reference",
        "internal_reference",
        "tester_id",
    )
    search_fields = (
        "serial_number",
        "client_reference",
        "internal_reference",
        "tester_id",
        "failure_type",
        "failure_message",
        "operator_name",
        "source_event_key",
    )
    ordering = ("-tested_at", "-id")