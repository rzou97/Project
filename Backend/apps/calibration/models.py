from django.db import models


class Instrument(models.Model):
    class TypeCode(models.TextChoices):
        CHARGE = "CHARGE", "Charge"
        DIELECTRIC = "DIELECTRIC", "Dielectric"
        GB_TESTER = "GB_TESTER", "GB TESTER"
        MESURE = "MESURE", "Mesure"
        MULTIMETRE = "MULTIMETRE", "Multimetre"
        OSCILL = "OSCILL", "Oscill"
        SWITCH = "SWITCH", "Switch"

    class CalibrationState(models.TextChoices):
        GOOD = "GOOD", "Bon"
        RESTRICTED = "RESTRICTED", "Utilisation avec restrictions"
        KO = "KO", "KO"

    class ConformityStatus(models.TextChoices):
        CONFORM = "CONFORM", "Conforme"
        NON_CONFORM = "NON_CONFORM", "Non conforme"

    class Status(models.TextChoices):
        VALID = "VALID", "Valid"
        DUE_SOON = "DUE_SOON", "Due Soon"
        OVERDUE = "OVERDUE", "Overdue"
        OUT_OF_SERVICE = "OUT_OF_SERVICE", "Out of Service"

    instrument_code = models.CharField(max_length=100, unique=True, db_index=True)
    designation = models.CharField(max_length=255)
    type_code = models.CharField(
        max_length=30,
        choices=TypeCode.choices,
        default=TypeCode.MESURE,
        db_index=True,
    )
    sub_family_code = models.CharField(max_length=100, blank=True, default="", db_index=True)
    serial_number = models.CharField(max_length=150, blank=True, default="")
    brand = models.CharField(max_length=150, blank=True, default="")
    affectation = models.CharField(max_length=150, blank=True, default="", db_index=True)
    location = models.CharField(max_length=150, blank=True, default="")
    assigned_to_asset = models.ForeignKey(
        "maintenance.MaintenanceAsset",
        on_delete=models.SET_NULL,
        related_name="instruments",
        null=True,
        blank=True,
    )
    calibration_frequency_months = models.PositiveIntegerField(default=12)
    last_calibration_date = models.DateField(null=True, blank=True)
    next_calibration_date = models.DateField(null=True, blank=True, db_index=True)
    calibration_state = models.CharField(
        max_length=20,
        choices=CalibrationState.choices,
        default=CalibrationState.GOOD,
        db_index=True,
    )
    conformity_status = models.CharField(
        max_length=20,
        choices=ConformityStatus.choices,
        default=ConformityStatus.CONFORM,
        db_index=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.VALID,
        db_index=True,
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "calibration_instrument"
        ordering = ["instrument_code"]

    def __str__(self):
        return f"{self.instrument_code} - {self.designation}"


class CalibrationRecord(models.Model):
    class CalibrationState(models.TextChoices):
        GOOD = "GOOD", "Bon"
        RESTRICTED = "RESTRICTED", "Utilisation avec restrictions"
        KO = "KO", "KO"

    class Result(models.TextChoices):
        CONFORM = "CONFORM", "Conform"
        NON_CONFORM = "NON_CONFORM", "Non Conform"

    instrument = models.ForeignKey(
        Instrument,
        on_delete=models.CASCADE,
        related_name="records",
    )
    provider_name = models.CharField(max_length=150, blank=True, default="")
    calibration_date = models.DateField(db_index=True)
    next_due_date = models.DateField(db_index=True)
    calibration_state = models.CharField(
        max_length=20,
        choices=CalibrationState.choices,
        default=CalibrationState.GOOD,
        db_index=True,
    )
    result = models.CharField(
        max_length=20,
        choices=Result.choices,
        db_index=True,
    )
    comment = models.TextField(blank=True, default="")
    report_file = models.FileField(upload_to="calibration_reports/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "calibration_record"
        ordering = ["-calibration_date", "-id"]

    def __str__(self):
        return f"{self.instrument.instrument_code} | {self.calibration_date}"
