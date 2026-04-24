from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Part(models.Model):
    class AffectationType(models.TextChoices):
        TESTER = "TESTER", "Tester"
        BAY = "BAY", "Bay"
        INSTRUMENT = "INSTRUMENT", "Instrument"
        GENERAL = "GENERAL", "General"

    class Unit(models.TextChoices):
        PIECE = "PIECE", "Pièce"
        METER = "METER", "Mètre"
        LITER = "LITER", "Litre"

    part_code = models.CharField(max_length=100, unique=True, db_index=True)
    designation = models.CharField(max_length=255, db_index=True)
    manufacturer = models.CharField(max_length=150, blank=True, default="")
    affectation_type = models.CharField(
        max_length=20,
        choices=AffectationType.choices,
        default=AffectationType.GENERAL,
        db_index=True,
    )
    affectation_value = models.CharField(max_length=150, blank=True, default="")
    unit = models.CharField(
        max_length=20,
        choices=Unit.choices,
        default=Unit.PIECE,
    )
    minimum_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pdr_part"
        ordering = ["part_code"]

    def __str__(self):
        return f"{self.part_code} - {self.designation}"

    def clean(self):
        super().clean()
        if self.part_code:
            self.part_code = self.part_code.strip().upper()
        if self.affectation_value:
            self.affectation_value = self.affectation_value.strip().upper()


class PartStock(models.Model):
    part = models.OneToOneField(
        Part,
        on_delete=models.CASCADE,
        related_name="stock",
    )
    current_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reserved_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    last_inventory_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pdr_part_stock"
        ordering = ["part__part_code"]

    def __str__(self):
        return f"{self.part.part_code} | {self.current_quantity}"

    @property
    def available_quantity(self):
        return self.current_quantity - self.reserved_quantity

    def clean(self):
        super().clean()
        if self.reserved_quantity > self.current_quantity:
            raise ValidationError(
                {"reserved_quantity": "reserved_quantity ne peut pas dépasser current_quantity."}
            )


class PartStockMovement(models.Model):
    class MovementType(models.TextChoices):
        IN = "IN", "Entrée"
        OUT = "OUT", "Sortie"
        ADJUSTMENT = "ADJUSTMENT", "Ajustement"

    class SourceType(models.TextChoices):
        CURATIVE = "CURATIVE", "Curative"
        PREVENTIVE = "PREVENTIVE", "Preventive"
        MANUAL = "MANUAL", "Manual"
        INVENTORY = "INVENTORY", "Inventory"

    part = models.ForeignKey(
        Part,
        on_delete=models.PROTECT,
        related_name="stock_movements",
    )
    movement_type = models.CharField(
        max_length=20,
        choices=MovementType.choices,
        db_index=True,
    )
    source_type = models.CharField(
        max_length=20,
        choices=SourceType.choices,
        default=SourceType.MANUAL,
        db_index=True,
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    comment = models.TextField(blank=True, default="")
    source_reference = models.CharField(max_length=150, blank=True, default="")
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="pdr_stock_movements",
        null=True,
        blank=True,
    )
    performed_at = models.DateTimeField(db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "pdr_part_stock_movement"
        ordering = ["-performed_at", "-id"]

    def __str__(self):
        return f"{self.part.part_code} | {self.movement_type} | {self.quantity}"