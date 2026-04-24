from django.contrib import admin
from .models import Part, PartStock, PartStockMovement

admin.site.register(Part)
admin.site.register(PartStock)
admin.site.register(PartStockMovement)