from django.db import models


class SyncCursor(models.Model):
    class Status(models.TextChoices):
        IDLE = "IDLE", "Idle"
        RUNNING = "RUNNING", "Running"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    source_table = models.CharField(max_length=150, unique=True, db_index=True)
    last_source_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    last_source_timestamp = models.DateTimeField(null=True, blank=True)

    sync_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IDLE,
        db_index=True,
    )

    last_synced_at = models.DateTimeField(null=True, blank=True)
    rows_processed = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "syncengine_sync_cursor"
        ordering = ["source_table"]

    def __str__(self):
        return f"{self.source_table} | {self.sync_status} | {self.last_source_id}"