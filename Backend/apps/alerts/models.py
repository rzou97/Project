from django.db import models


class AlertRule(models.Model):
    class AlertType(models.TextChoices):
        REPEATED_DEFECT_MESSAGE = "REPEATED_DEFECT_MESSAGE", "Repeated Defect Message"
        HIGH_FAILURE_RATE = "HIGH_FAILURE_RATE", "High Failure Rate"
        LOW_FPY = "LOW_FPY", "Low FPY"

    class Severity(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"
        CRITICAL = "CRITICAL", "Critical"

    name = models.CharField(max_length=150, unique=True)
    alert_type = models.CharField(
        max_length=30,
        choices=AlertType.choices,
        db_index=True,
    )
    threshold_value = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    time_window_minutes = models.PositiveIntegerField(default=60)
    consecutive_count = models.PositiveIntegerField(default=3)
    severity = models.CharField(
        max_length=20,
        choices=Severity.choices,
        default=Severity.MEDIUM,
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alerts_alert_rule"
        ordering = ["name"]

    def __str__(self):
        return self.name


class AlertEvent(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        ACKNOWLEDGED = "ACKNOWLEDGED", "Acknowledged"
        RESOLVED = "RESOLVED", "Resolved"

    rule = models.ForeignKey(
        AlertRule,
        on_delete=models.PROTECT,
        related_name="events",
    )
    asset = models.ForeignKey(
        "maintenance.MaintenanceAsset",
        on_delete=models.PROTECT,
        related_name="alert_events",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    severity = models.CharField(
        max_length=20,
        choices=AlertRule.Severity.choices,
        db_index=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )
    entity_type = models.CharField(max_length=50, default="TESTER", db_index=True)
    entity_key = models.CharField(max_length=150, db_index=True)

    triggered_at = models.DateTimeField(db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alerts_alert_event"
        ordering = ["-triggered_at", "-id"]

    def __str__(self):
        return f"{self.rule.name} | {self.entity_key} | {self.status}"