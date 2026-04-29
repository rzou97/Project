from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.failures.models import FailureCase


class RepairTicket(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        WAITING_RETEST = "WAITING_RETEST", "Waiting Retest"
        CLOSED = "CLOSED", "Closed"
        CANCELLED = "CANCELLED", "Cancelled"

    failure_case = models.ForeignKey(
        FailureCase,
        on_delete=models.CASCADE,
        related_name="repair_tickets",
    )
    ticket_code = models.CharField(max_length=100, unique=True, db_index=True)
    ticket_status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )
    cycle_number = models.PositiveIntegerField(default=1, db_index=True)
    opened_at = models.DateTimeField(db_index=True)
    closed_at = models.DateTimeField(null=True, blank=True, db_index=True)
    repair_effectiveness = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "repairs_repair_ticket"
        ordering = ["-opened_at", "-id"]
        indexes = [
            models.Index(fields=["ticket_code"]),
            models.Index(fields=["ticket_status"]),
            models.Index(fields=["cycle_number"]),
            models.Index(fields=["opened_at"]),
        ]

    def __str__(self):
        return f"{self.ticket_code} | {self.ticket_status}"

    def clean(self):
        super().clean()

        if self.cycle_number < 1:
            raise ValidationError({"cycle_number": "cycle_number doit etre superieur ou egal a 1."})

        if self.closed_at and self.closed_at < self.opened_at:
            raise ValidationError({"closed_at": "closed_at doit etre superieur ou egal a opened_at."})


class RepairAction(models.Model):
    class Progress(models.TextChoices):
        PENDING = "PENDING", "Pending"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        DONE = "DONE", "Done"
        WAITING_PARTS = "WAITING_PARTS", "Waiting Parts"
        WAITING_RETEST = "WAITING_RETEST", "Waiting Retest"

    repair_ticket = models.ForeignKey(
        RepairTicket,
        on_delete=models.CASCADE,
        related_name="repair_actions",
        null=True,
        blank=True,
        default=None,
    )
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="repair_actions",
    )

    defect_type = models.CharField(max_length=150, blank=True, default="", db_index=True)
    observed_defect = models.TextField(blank=True, default="")
    detected_cause = models.TextField(blank=True, default="")
    action_taken = models.TextField()
    action_progress = models.CharField(
        max_length=30,
        choices=Progress.choices,
        default=Progress.PENDING,
        db_index=True,
    )
    performed_at = models.DateTimeField(db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "repairs_repair_action"
        ordering = ["-performed_at", "-id"]
        indexes = [
            models.Index(fields=["repair_ticket"]),
            models.Index(fields=["technician"]),
            models.Index(fields=["action_progress"]),
            models.Index(fields=["performed_at"]),
            models.Index(fields=["defect_type"]),
        ]

    def __str__(self):
        ticket_code = self.repair_ticket.ticket_code if self.repair_ticket_id else "NO_TICKET"
        return f"{ticket_code} | {self.action_progress} | {self.performed_at}"

    @property
    def failure_case(self):
        return self.repair_ticket.failure_case if self.repair_ticket_id else None

    @property
    def board(self):
        return self.repair_ticket.failure_case.board if self.repair_ticket_id else None

    @property
    def serial_number(self):
        return self.repair_ticket.failure_case.serial_number if self.repair_ticket_id else ""

    def clean(self):
        super().clean()

        if self.performed_at and self.repair_ticket_id and self.performed_at < self.repair_ticket.opened_at:
            raise ValidationError({"performed_at": "performed_at doit etre superieur ou egal a opened_at du ticket."})
