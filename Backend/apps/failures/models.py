from django.core.exceptions import ValidationError
from django.db import models

from apps.boards.models import Board
from apps.testresults.models import TestResult


class FailureCase(models.Model):
    class Status(models.TextChoices):
        IN_DEFECT = "IN_DEFECT", "In Defect"
        IN_REPAIR = "IN_REPAIR", "In Repair"
        WAITING_RETEST = "WAITING_RETEST", "Waiting Retest"
        REPAIRED = "REPAIRED", "Repaired"

    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="failure_cases",
    )
    source_test_result = models.ForeignKey(
        TestResult,
        on_delete=models.PROTECT,
        related_name="failure_cases",
    )

    serial_number = models.CharField(max_length=100, db_index=True)
    client_reference = models.CharField(max_length=100, blank=True, default="", db_index=True)
    internal_reference = models.CharField(max_length=100, blank=True, default="", db_index=True)

    failure_status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.IN_DEFECT,
        db_index=True,
    )

    detected_in_phase = models.CharField(
        max_length=30,
        choices=TestResult.Phase.choices,
        db_index=True,
    )
    detected_on_tester = models.CharField(max_length=100, db_index=True)

    failure_type = models.CharField(max_length=150, blank=True, default="", db_index=True)
    failure_message = models.TextField(blank=True, default="")

    opened_at = models.DateTimeField(db_index=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "failures_failure_case"
        ordering = ["-opened_at", "-id"]
        indexes = [
            models.Index(fields=["serial_number"]),
            models.Index(fields=["client_reference"]),
            models.Index(fields=["internal_reference"]),
            models.Index(fields=["failure_status"]),
            models.Index(fields=["detected_in_phase"]),
            models.Index(fields=["detected_on_tester"]),
            models.Index(fields=["opened_at"]),
        ]

    def __str__(self):
        return f"{self.serial_number} | {self.failure_status} | {self.detected_in_phase}"

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

        if self.source_test_result_id:
            tr = self.source_test_result

            if self.board_id and tr.board_id != self.board_id:
                raise ValidationError(
                    {"source_test_result": "Le test source doit appartenir au même board."}
                )

            if tr.serial_number != self.serial_number:
                raise ValidationError(
                    {"serial_number": "Le serial_number doit correspondre au test source."}
                )

            if self.client_reference and tr.client_reference != self.client_reference:
                raise ValidationError(
                    {"client_reference": "La client_reference doit correspondre au test source."}
                )

            if self.internal_reference and tr.internal_reference != self.internal_reference:
                raise ValidationError(
                    {"internal_reference": "La internal_reference doit correspondre au test source."}
                )

            if tr.test_phase != self.detected_in_phase:
                raise ValidationError(
                    {"detected_in_phase": "La phase doit correspondre au test source."}
                )

            if tr.tester_id != self.detected_on_tester:
                raise ValidationError(
                    {"detected_on_tester": "Le testeur doit correspondre au test source."}
                )

        if self.closed_at and self.closed_at < self.opened_at:
            raise ValidationError(
                {"closed_at": "closed_at doit être supérieur ou égal à opened_at."}
            )