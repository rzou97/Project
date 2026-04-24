from django.contrib import admin

from .models import Board


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "serial_number",
        "client_reference",
        "internal_reference",
        "current_status",
        "first_seen_at",
        "last_seen_at",
        "created_at",
    )
    list_filter = ("current_status", "client_reference", "internal_reference")
    search_fields = ("serial_number", "client_reference", "internal_reference")
    ordering = ("-updated_at",)