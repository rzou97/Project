from django.core.exceptions import ValidationError
from django.db import models

from apps.boards.models import Board


class TestResult(models.Model):
    class Phase(models.TextChoices):
        BOARD_TEST = "BOARD_TEST", "Test carte"
        NORMATIVE_TEST = "NORMATIVE_TEST", "Test normatif"
        BURN_IN_TEST = "BURN_IN_TEST", "Test déverminage"
        LEAK_TEST = "LEAK_TEST", "Test étanchéité"
        FINAL_TEST = "FINAL_TEST", "Test final"

    class Result(models.TextChoices):
        FAILED = "FAILED", "Failed"
        PASSED = "PASSED", "Passed"
        ERROR = "ERROR", "Error"
        TERMINATED = "TERMINATED", "Terminated"

    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="test_results",
    )

    serial_number = models.CharField(max_length=100, db_index=True)
    client_reference = models.CharField(max_length=100, blank=True, default="", db_index=True)
    internal_reference = models.CharField(max_length=100, blank=True, default="", db_index=True)

    operator_name = models.CharField(max_length=150, blank=True, default="")
    tester_id = models.CharField(max_length=100, db_index=True)

    test_phase = models.CharField(
        max_length=30,
        choices=Phase.choices,
        db_index=True,
    )
    result = models.CharField(
        max_length=20,
        choices=Result.choices,
        db_index=True,
    )

    failure_type = models.CharField(max_length=150, blank=True, default="", db_index=True)
    failure_message = models.TextField(blank=True, default="")

    tested_at = models.DateTimeField(db_index=True)

    source_event_key = models.CharField(max_length=64, unique=True, db_index=True)
    raw_ingested_ts = models.DateTimeField(null=True, blank=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "testresults_test_result"
        ordering = ["-tested_at", "-id"]
        indexes = [
            models.Index(fields=["serial_number"]),
            models.Index(fields=["client_reference"]),
            models.Index(fields=["internal_reference"]),
            models.Index(fields=["test_phase"]),
            models.Index(fields=["tester_id"]),
            models.Index(fields=["result"]),
            models.Index(fields=["tested_at"]),
            models.Index(fields=["raw_ingested_ts"]),
        ]

    def __str__(self):
        return f"{self.serial_number} | {self.test_phase} | {self.result}"

    def clean(self):
        super().clean()

        if self.serial_number:
            self.serial_number = self.serial_number.strip().upper()

        if self.client_reference:
            self.client_reference = self.client_reference.strip().upper()

        if self.internal_reference:
            self.internal_reference = self.internal_reference.strip().upper()

        if self.board_id:
            if self.board.serial_number != self.serial_number:
                raise ValidationError(
                    {"serial_number": "Le serial_number doit correspondre au board lié."}
                )

            if self.client_reference and self.board.client_reference != self.client_reference:
                raise ValidationError(
                    {"client_reference": "La client_reference doit correspondre au board lié."}
                )

            if self.internal_reference and self.board.internal_reference != self.internal_reference:
                raise ValidationError(
                    {"internal_reference": "La internal_reference doit correspondre au board lié."}
                )