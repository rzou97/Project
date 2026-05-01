from django.contrib import admin

from apps.intelligence.models import (
    FailureEnrichment,
    RepairHistory,
    RepairPrediction,
    RepairProcedureTemplate,
)

admin.site.register(RepairHistory)
admin.site.register(RepairProcedureTemplate)
admin.site.register(FailureEnrichment)
admin.site.register(RepairPrediction)
