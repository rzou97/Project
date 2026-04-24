from django.contrib import admin

from .models import SyncCursor


@admin.register(SyncCursor)
class SyncCursorAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "source_table",
        "last_source_id",
        "sync_status",
        "last_synced_at",
        "rows_processed",
        "updated_at",
    )
    list_filter = ("sync_status", "source_table")
    search_fields = ("source_table", "error_message")
    ordering = ("source_table",)