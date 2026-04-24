from rest_framework import serializers

from apps.pdr.models import Part, PartStock, PartStockMovement


class PartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = (
            "id",
            "part_code",
            "designation",
            "manufacturer",
            "affectation_type",
            "affectation_value",
            "unit",
            "minimum_stock",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class PartStockSerializer(serializers.ModelSerializer):
    available_quantity = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = PartStock
        fields = (
            "id",
            "part",
            "current_quantity",
            "reserved_quantity",
            "available_quantity",
            "last_inventory_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "available_quantity", "created_at", "updated_at")


class PartStockMovementSerializer(serializers.ModelSerializer):
    performer_matricule = serializers.CharField(source="performed_by.matricule", read_only=True)

    class Meta:
        model = PartStockMovement
        fields = (
            "id",
            "part",
            "movement_type",
            "source_type",
            "quantity",
            "comment",
            "source_reference",
            "performed_by",
            "performer_matricule",
            "performed_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "performed_by", "performer_matricule")