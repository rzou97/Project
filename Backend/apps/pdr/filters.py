import django_filters

from apps.pdr.models import Part, PartStockMovement


class PartFilter(django_filters.FilterSet):
    part_code = django_filters.CharFilter(field_name="part_code", lookup_expr="icontains")
    designation = django_filters.CharFilter(field_name="designation", lookup_expr="icontains")
    manufacturer = django_filters.CharFilter(field_name="manufacturer", lookup_expr="icontains")
    affectation_type = django_filters.ChoiceFilter(field_name="affectation_type", choices=Part.AffectationType.choices)
    affectation_value = django_filters.CharFilter(field_name="affectation_value", lookup_expr="icontains")
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = Part
        fields = [
            "part_code",
            "designation",
            "manufacturer",
            "affectation_type",
            "affectation_value",
            "is_active",
        ]


class PartStockMovementFilter(django_filters.FilterSet):
    part = django_filters.NumberFilter(field_name="part_id")
    movement_type = django_filters.ChoiceFilter(field_name="movement_type", choices=PartStockMovement.MovementType.choices)
    source_type = django_filters.ChoiceFilter(field_name="source_type", choices=PartStockMovement.SourceType.choices)
    performed_at_after = django_filters.DateTimeFilter(field_name="performed_at", lookup_expr="gte")
    performed_at_before = django_filters.DateTimeFilter(field_name="performed_at", lookup_expr="lte")

    class Meta:
        model = PartStockMovement
        fields = ["part", "movement_type", "source_type"]