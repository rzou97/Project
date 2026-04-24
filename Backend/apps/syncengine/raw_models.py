from django.db import models


class RawTestEventEnriched(models.Model):
    sn_global = models.CharField(max_length=150)
    reference_client = models.CharField(max_length=100, blank=True, default="")
    reference_interne = models.CharField(max_length=100, blank=True, default="")
    operator_name = models.CharField(max_length=150, blank=True, default="")
    station_id = models.CharField(max_length=100, blank=True, default="")
    defect_type = models.CharField(max_length=150, blank=True, default="")
    defect_type_norm = models.CharField(max_length=150, blank=True, default="")
    defect_message = models.TextField(blank=True, default="")
    defect_exact_norm = models.CharField(max_length=150, blank=True, default="")
    event_ts = models.DateTimeField(null=True, blank=True)
    ingested_ts = models.DateTimeField(null=True, blank=True)
    phase = models.CharField(max_length=100, blank=True, default="")
    result_norm = models.CharField(max_length=50, blank=True, default="")

    class Meta:
        managed = False
        db_table = "test_events_base_enriched"