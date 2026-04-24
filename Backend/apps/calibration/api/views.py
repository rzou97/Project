from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.calibration.filters import CalibrationRecordFilter, InstrumentFilter
from apps.calibration.models import CalibrationRecord, Instrument
from .serializers import CalibrationRecordSerializer, InstrumentSerializer


class InstrumentViewSet(ModelViewSet):
    queryset = Instrument.objects.select_related("assigned_to_asset").all()
    serializer_class = InstrumentSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = InstrumentFilter
    search_fields = [
        "instrument_code",
        "designation",
        "type_code",
        "sub_family_code",
        "serial_number",
        "brand",
        "affectation",
        "location",
    ]
    ordering_fields = [
        "instrument_code",
        "designation",
        "type_code",
        "brand",
        "next_calibration_date",
        "calibration_state",
        "conformity_status",
        "created_at",
        "updated_at",
    ]
    ordering = ["instrument_code"]


class CalibrationRecordViewSet(ModelViewSet):
    queryset = CalibrationRecord.objects.select_related("instrument").all()
    serializer_class = CalibrationRecordSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = CalibrationRecordFilter
    search_fields = ["instrument__instrument_code", "provider_name", "comment"]
    ordering_fields = ["calibration_date", "next_due_date", "calibration_state", "result", "created_at", "updated_at"]
    ordering = ["-calibration_date", "-id"]

    def perform_create(self, serializer):
        record = serializer.save()
        self._sync_instrument_status(record)

    def perform_update(self, serializer):
        record = serializer.save()
        self._sync_instrument_status(record)

    def _sync_instrument_status(self, record: CalibrationRecord) -> None:
        instrument = record.instrument
        instrument.last_calibration_date = record.calibration_date
        instrument.next_calibration_date = record.next_due_date
        instrument.calibration_state = record.calibration_state
        instrument.conformity_status = record.result

        if record.calibration_state == CalibrationRecord.CalibrationState.GOOD:
            instrument.status = Instrument.Status.VALID
        elif record.calibration_state == CalibrationRecord.CalibrationState.RESTRICTED:
            instrument.status = Instrument.Status.DUE_SOON
        else:
            instrument.status = Instrument.Status.OUT_OF_SERVICE

        instrument.save(
            update_fields=[
                "last_calibration_date",
                "next_calibration_date",
                "calibration_state",
                "conformity_status",
                "status",
                "updated_at",
            ]
        )
