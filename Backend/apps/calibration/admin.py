from django.contrib import admin
from .models import Instrument, CalibrationRecord

admin.site.register(Instrument)
admin.site.register(CalibrationRecord)