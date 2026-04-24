from rest_framework import serializers

from apps.calibration.models import CalibrationRecord, Instrument


class InstrumentSerializer(serializers.ModelSerializer):
    asset_code = serializers.CharField(source="assigned_to_asset.asset_code", read_only=True)

    class Meta:
        model = Instrument
        fields = (
            "id",
            "instrument_code",
            "designation",
            "type_code",
            "sub_family_code",
            "serial_number",
            "brand",
            "affectation",
            "location",
            "assigned_to_asset",
            "asset_code",
            "calibration_frequency_months",
            "last_calibration_date",
            "next_calibration_date",
            "calibration_state",
            "conformity_status",
            "status",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "asset_code")


class CalibrationRecordSerializer(serializers.ModelSerializer):
    instrument_code = serializers.CharField(source="instrument.instrument_code", read_only=True)

    class Meta:
        model = CalibrationRecord
        fields = (
            "id",
            "instrument",
            "instrument_code",
            "provider_name",
            "calibration_date",
            "next_due_date",
            "calibration_state",
            "result",
            "comment",
            "report_file",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "instrument_code")
