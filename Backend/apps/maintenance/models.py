from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class MaintenanceAsset(models.Model):
    class AssetType(models.TextChoices):
        TESTER = "TESTER", "Tester"
        BAY = "BAY", "Bay"
        BENCH = "BENCH", "Bench"
        INSTRUMENT = "INSTRUMENT", "Instrument"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        IN_BREAKDOWN = "IN_BREAKDOWN", "In Breakdown"
        IN_MAINTENANCE = "IN_MAINTENANCE", "In Maintenance"
        OUT_OF_SERVICE = "OUT_OF_SERVICE", "Out of Service"

    asset_code = models.CharField(max_length=100, unique=True, db_index=True)
    asset_name = models.CharField(max_length=255)
    asset_type = models.CharField(
        max_length=20,
        choices=AssetType.choices,
        db_index=True,
    )
    tester_id = models.CharField(max_length=100, blank=True, default="", db_index=True)
    location = models.CharField(max_length=150, blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    manufacturer = models.CharField(max_length=150, blank=True, default="")
    model = models.CharField(max_length=150, blank=True, default="")
    serial_number = models.CharField(max_length=150, blank=True, default="")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "maintenance_asset"
        ordering = ["asset_code"]

    def __str__(self):
        return f"{self.asset_code} - {self.asset_name}"

    def clean(self):
        super().clean()
        if self.asset_code:
            self.asset_code = self.asset_code.strip().upper()
        if self.tester_id:
            self.tester_id = self.tester_id.strip().upper()


class CurativeTicket(models.Model):
    class TriggerType(models.TextChoices):
        REPEATED_DEFECT_MESSAGE = "REPEATED_DEFECT_MESSAGE", "Repeated Defect Message"
        HIGH_FAILURE_RATE = "HIGH_FAILURE_RATE", "High Failure Rate"
        LOW_FPY = "LOW_FPY", "Low FPY"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        WAITING_VALIDATION = "WAITING_VALIDATION", "Waiting Validation"
        CLOSED = "CLOSED", "Closed"

    asset = models.ForeignKey(
        "maintenance.MaintenanceAsset",
        on_delete=models.PROTECT,
        related_name="curative_tickets",
    )
    source_alert_event = models.ForeignKey(
        "alerts.AlertEvent",
        on_delete=models.SET_NULL,
        related_name="curative_tickets",
        null=True,
        blank=True,
    )

    ticket_code = models.CharField(max_length=100, unique=True, db_index=True)
    trigger_type = models.CharField(
        max_length=30,
        choices=TriggerType.choices,
        db_index=True,
    )
    title = models.CharField(max_length=255)
    symptom = models.TextField(blank=True, default="")
    failure_cause = models.TextField(blank=True, default="")
    comment = models.TextField(blank=True, default="")

    downtime_start = models.DateTimeField(db_index=True)
    downtime_end = models.DateTimeField(null=True, blank=True)
    downtime_minutes = models.PositiveIntegerField(default=0)

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )
    opened_by_system = models.BooleanField(default=True)

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="assigned_curative_tickets",
        null=True,
        blank=True,
    )
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="closed_curative_tickets",
        null=True,
        blank=True,
    )

    opened_at = models.DateTimeField(db_index=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "maintenance_curative_ticket"
        ordering = ["-opened_at", "-id"]

    def __str__(self):
        return f"{self.ticket_code} | {self.asset.asset_code} | {self.status}"

    def clean(self):
        super().clean()
        if self.closed_at and self.closed_at < self.opened_at:
            raise ValidationError(
                {"closed_at": "closed_at doit être supérieur ou égal à opened_at."}
            )
        if self.downtime_end and self.downtime_end < self.downtime_start:
            raise ValidationError(
                {"downtime_end": "downtime_end doit être supérieur ou égal à downtime_start."}
            )


class CurativeAction(models.Model):
    ticket = models.ForeignKey(
        CurativeTicket,
        on_delete=models.CASCADE,
        related_name="actions",
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="curative_actions",
    )
    diagnosis = models.TextField(blank=True, default="")
    failure_cause = models.TextField(blank=True, default="")
    action_taken = models.TextField()
    comment = models.TextField(blank=True, default="")
    started_at = models.DateTimeField(db_index=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "maintenance_curative_action"
        ordering = ["-started_at", "-id"]

    def __str__(self):
        return f"{self.ticket.ticket_code} | {self.performed_by}"

    def clean(self):
        super().clean()
        if self.ended_at and self.ended_at < self.started_at:
            raise ValidationError(
                {"ended_at": "ended_at doit être supérieur ou égal à started_at."}
            )


class CurativePart(models.Model):
    ticket = models.ForeignKey(
        CurativeTicket,
        on_delete=models.CASCADE,
        related_name="parts",
    )
    part = models.ForeignKey(
        "pdr.Part",
        on_delete=models.PROTECT,
        related_name="curative_usages",
    )
    planned_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    consumed_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    comment = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "maintenance_curative_part"
        ordering = ["ticket_id", "part__part_code"]

    def __str__(self):
        return f"{self.ticket.ticket_code} | {self.part.part_code}"
    
class PreventivePlan(models.Model):
    class Frequency(models.TextChoices):
        DAILY = "DAILY", "Daily"
        WEEKLY = "WEEKLY", "Weekly"
        MONTHLY = "MONTHLY", "Monthly"
        QUARTERLY = "QUARTERLY", "Quarterly"
        YEARLY = "YEARLY", "Yearly"

    asset = models.ForeignKey(
        MaintenanceAsset,
        on_delete=models.CASCADE,
        related_name="preventive_plans",
        null=True,
        blank=True,
        default=None,
    )
    plan_code = models.CharField(max_length=100, unique=True, db_index=True)
    plan_name = models.CharField(max_length=255)
    frequency = models.CharField(
        max_length=50,
        choices=Frequency.choices,
        db_index=True,
    )
    description = models.TextField(blank=True, default="")
    estimated_duration_minutes = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "maintenance_preventive_plan"
        ordering = ["plan_code"]

    def __str__(self):
        return f"{self.plan_code} - {self.plan_name}"


class PreventiveTask(models.Model):
    plan = models.ForeignKey(
        PreventivePlan,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    step_order = models.PositiveIntegerField()
    task_label = models.CharField(max_length=255)
    instruction = models.TextField(blank=True, default="")
    is_mandatory = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "maintenance_preventive_task"
        ordering = ["plan", "step_order"]
        unique_together = [("plan", "step_order")]

    def __str__(self):
        return f"{self.plan.plan_code} | {self.step_order} | {self.task_label}"


class PreventivePart(models.Model):
    plan = models.ForeignKey(
        PreventivePlan,
        on_delete=models.CASCADE,
        related_name="parts",
    )
    part = models.ForeignKey(
        "pdr.Part",
        on_delete=models.PROTECT,
        related_name="preventive_plans",
    )
    planned_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    comment = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "maintenance_preventive_part"
        ordering = ["plan", "part__part_code"]

    def __str__(self):
        return f"{self.plan.plan_code} | {self.part.part_code}"


class PreventiveSchedule(models.Model):
    class Status(models.TextChoices):
        PLANNED = "PLANNED", "Planned"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        DONE = "DONE", "Done"
        OVERDUE = "OVERDUE", "Overdue"
        CANCELLED = "CANCELLED", "Cancelled"

    plan = models.ForeignKey(
        PreventivePlan,
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    scheduled_for = models.DateTimeField(db_index=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED,
        db_index=True,
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="preventive_schedules",
        null=True,
        blank=True,
    )
    performed_at = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "maintenance_preventive_schedule"
        ordering = ["-scheduled_for", "-id"]

    def __str__(self):
        return f"{self.plan.plan_code} | {self.scheduled_for} | {self.status}"


class PreventiveExecutionPart(models.Model):
    schedule = models.ForeignKey(
        PreventiveSchedule,
        on_delete=models.CASCADE,
        related_name="execution_parts",
    )
    part = models.ForeignKey(
        "pdr.Part",
        on_delete=models.PROTECT,
        related_name="preventive_execution_parts",
    )
    planned_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    consumed_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    comment = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "maintenance_preventive_execution_part"
        ordering = ["schedule", "part__part_code"]

    def __str__(self):
        return f"{self.schedule.id} | {self.part.part_code}"
