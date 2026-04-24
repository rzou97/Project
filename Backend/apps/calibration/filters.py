import django_filters

from apps.calibration.models import CalibrationRecord, Instrument


class InstrumentFilter(django_filters.FilterSet):
    instrument_code = django_filters.CharFilter(field_name="instrument_code", lookup_expr="icontains")
    designation = django_filters.CharFilter(field_name="designation", lookup_expr="icontains")
    type_code = django_filters.ChoiceFilter(field_name="type_code", choices=Instrument.TypeCode.choices)
    sub_family_code = django_filters.CharFilter(field_name="sub_family_code", lookup_expr="icontains")
    brand = django_filters.CharFilter(field_name="brand", lookup_expr="icontains")
    affectation = django_filters.CharFilter(field_name="affectation", lookup_expr="icontains")
    calibration_state = django_filters.ChoiceFilter(
        field_name="calibration_state", choices=Instrument.CalibrationState.choices
    )
    conformity_status = django_filters.ChoiceFilter(
        field_name="conformity_status", choices=Instrument.ConformityStatus.choices
    )
    status = django_filters.ChoiceFilter(field_name="status", choices=Instrument.Status.choices)
    is_active = django_filters.BooleanFilter(field_name="is_active")
    next_calibration_date_after = django_filters.DateFilter(field_name="next_calibration_date", lookup_expr="gte")
    next_calibration_date_before = django_filters.DateFilter(field_name="next_calibration_date", lookup_expr="lte")

    class Meta:
        model = Instrument
        fields = [
            "instrument_code",
            "designation",
            "type_code",
            "sub_family_code",
            "brand",
            "affectation",
            "calibration_state",
            "conformity_status",
            "status",
            "is_active",
        ]


class CalibrationRecordFilter(django_filters.FilterSet):
    instrument = django_filters.NumberFilter(field_name="instrument_id")
    calibration_state = django_filters.ChoiceFilter(
        field_name="calibration_state", choices=CalibrationRecord.CalibrationState.choices
    )
    result = django_filters.ChoiceFilter(field_name="result", choices=CalibrationRecord.Result.choices)
    calibration_date_after = django_filters.DateFilter(field_name="calibration_date", lookup_expr="gte")
    calibration_date_before = django_filters.DateFilter(field_name="calibration_date", lookup_expr="lte")

    class Meta:
        model = CalibrationRecord
        fields = ["instrument", "calibration_state", "result"]
