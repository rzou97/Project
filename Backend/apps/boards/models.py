from django.core.exceptions import ValidationError
from django.db import models


class Board(models.Model):
    class Status(models.TextChoices):
        HEALTHY = "HEALTHY", "Healthy"
        IN_DEFECT = "IN_DEFECT", "In Defect"
        IN_REPAIR = "IN_REPAIR", "In Repair"
        WAITING_RETEST = "WAITING_RETEST", "Waiting Retest"
        REPAIRED = "REPAIRED", "Repaired"

    serial_number = models.CharField(max_length=100, unique=True, db_index=True)
    client_reference = models.CharField(max_length=100, blank=True, default="", db_index=True)
    internal_reference = models.CharField(max_length=100, blank=True, default="", db_index=True)

    current_status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.HEALTHY,
        db_index=True,
    )

    first_seen_at = models.DateTimeField()
    last_seen_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "boards_board"
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["serial_number"]),
            models.Index(fields=["client_reference"]),
            models.Index(fields=["internal_reference"]),
            models.Index(fields=["current_status"]),
            models.Index(fields=["last_seen_at"]),
        ]

    def __str__(self):
        return f"{self.serial_number} | {self.internal_reference}"

    def clean(self):
        super().clean()

        if self.serial_number:
            self.serial_number = self.serial_number.strip().upper()

        if self.client_reference:
            self.client_reference = self.client_reference.strip().upper()

        if self.internal_reference:
            self.internal_reference = self.internal_reference.strip().upper()

        if self.first_seen_at and self.last_seen_at and self.last_seen_at < self.first_seen_at:
            raise ValidationError(
                {"last_seen_at": "last_seen_at doit être supérieur ou égal à first_seen_at."}
            )