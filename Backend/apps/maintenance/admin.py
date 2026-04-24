from django.contrib import admin
from .models import (
    MaintenanceAsset,
    CurativeTicket,
    CurativeAction,
    CurativePart,
    PreventivePlan,
    PreventiveTask,
    PreventivePart,
    PreventiveSchedule,
    PreventiveExecutionPart,
)

admin.site.register(MaintenanceAsset)
admin.site.register(CurativeTicket)
admin.site.register(CurativeAction)
admin.site.register(CurativePart)
admin.site.register(PreventivePlan)
admin.site.register(PreventiveTask)
admin.site.register(PreventivePart)
admin.site.register(PreventiveSchedule)
admin.site.register(PreventiveExecutionPart)