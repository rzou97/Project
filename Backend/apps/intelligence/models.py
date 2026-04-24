from django.core.exceptions import ValidationError
from django.db import models


class RepairHistory(models.Model):
    failure_case = models.ForeignKey(
        "failures.FailureCase",
        on_delete=models.CASCADE,
        related_name="repair_histories",
    )
    repair_ticket = models.ForeignKey(
        "repairs.RepairTicket",
        on_delete=models.CASCADE,
        related_name="repair_histories",
        null=True,
        blank=True,
        default=None,
    )
    repair_action = models.ForeignKey(
        "repairs.RepairAction",
        on_delete=models.CASCADE,
        related_name="repair_histories",
        null=True,
        blank=True,
        default=None,
    )
    source_test_result = models.ForeignKey(
        "testresults.TestResult",
        on_delete=models.PROTECT,
        related_name="repair_histories",
        null=True,
        blank=True,
        default=None,
    )

    serial_number = models.CharField(max_length=100, db_index=True)
    client_reference = models.CharField(max_length=100, blank=True, default="", db_index=True)
    internal_reference = models.CharField(max_length=100, blank=True, default="", db_index=True)

    detected_in_phase = models.CharField(max_length=30, db_index=True)
    detected_on_tester = models.CharField(max_length=100, db_index=True)
    failure_type = models.CharField(max_length=150, blank=True, default="", db_index=True)
    failure_message = models.TextField(blank=True, default="")

    technician_matricule = models.CharField(max_length=100, blank=True, default="", db_index=True)
    detected_cause = models.TextField(blank=True, default="")
    action_taken = models.TextField(blank=True, default="")
    retest_result = models.CharField(max_length=50, blank=True, default="")
    final_outcome = models.CharField(max_length=50, default="IN_PROGRESS", db_index=True)
    repair_cycle_count = models.PositiveIntegerField(default=1, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "intelligence_repair_history"
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["serial_number"]),
            models.Index(fields=["failure_type"]),
            models.Index(fields=["detected_on_tester"]),
            models.Index(fields=["final_outcome"]),
            models.Index(fields=["repair_cycle_count"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.serial_number} | {self.failure_type} | {self.final_outcome}"

    def clean(self):
        super().clean()

        if self.repair_ticket_id and self.failure_case_id and self.repair_ticket.failure_case_id != self.failure_case_id:
            raise ValidationError({"repair_ticket": "repair_ticket doit etre lie au meme failure_case."})

        if self.repair_action_id and self.repair_ticket_id and self.repair_action.repair_ticket_id != self.repair_ticket_id:
            raise ValidationError({"repair_action": "repair_action doit etre lie a ce repair_ticket."})

        if self.serial_number and self.failure_case_id and self.failure_case.serial_number != self.serial_number:
            raise ValidationError({"serial_number": "serial_number doit correspondre au failure_case."})

        if self.repair_cycle_count < 1:
            raise ValidationError({"repair_cycle_count": "repair_cycle_count doit etre superieur ou egal a 1."})


class RepairProcedureTemplate(models.Model):
    procedure_name = models.CharField(max_length=200, db_index=True)
    failure_type = models.CharField(max_length=150, db_index=True)
    failure_signature = models.CharField(max_length=255, blank=True, default="", db_index=True)
    recommended_steps = models.JSONField(default=list, blank=True)
    recommended_parts = models.JSONField(default=list, blank=True)
    success_rate = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    version = models.CharField(max_length=30, default="v1")
    generated_at = models.DateTimeField(db_index=True)

    class Meta:
        db_table = "intelligence_repair_procedure_template"
        ordering = ["-generated_at", "-id"]
        indexes = [
            models.Index(fields=["failure_type"]),
            models.Index(fields=["failure_signature"]),
            models.Index(fields=["generated_at"]),
        ]

    def __str__(self):
        return f"{self.procedure_name} | {self.failure_type} | {self.version}"


class RepairPrediction(models.Model):
    prediction_type = models.CharField(max_length=100, db_index=True)
    target_serial_number = models.CharField(max_length=100, db_index=True)
    predicted_cause = models.TextField(blank=True, default="")
    recommended_action = models.TextField(blank=True, default="")
    recommended_procedure = models.ForeignKey(
        RepairProcedureTemplate,
        on_delete=models.SET_NULL,
        related_name="predictions",
        null=True,
        blank=True,
    )
    confidence_score = models.DecimalField(max_digits=6, decimal_places=4)
    predicted_at = models.DateTimeField(db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "intelligence_repair_prediction"
        ordering = ["-predicted_at", "-id"]
        indexes = [
            models.Index(fields=["prediction_type"]),
            models.Index(fields=["target_serial_number"]),
            models.Index(fields=["predicted_at"]),
        ]

    def __str__(self):
        return f"{self.prediction_type} | {self.target_serial_number} | {self.confidence_score}"
