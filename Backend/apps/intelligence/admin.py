from django.contrib import admin

from apps.intelligence.models import RepairHistory, RepairPrediction, RepairProcedureTemplate

admin.site.register(RepairHistory)
admin.site.register(RepairProcedureTemplate)
admin.site.register(RepairPrediction)
