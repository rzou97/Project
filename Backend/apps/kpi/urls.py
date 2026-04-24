from django.urls import path

from apps.kpi.api.views import TestersCurrentStatusView, TestersFpyInstantView

urlpatterns = [
    path("testers-fpy-instant/", TestersFpyInstantView.as_view(), name="kpi-testers-fpy-instant"),
    path("testers-current-status/", TestersCurrentStatusView.as_view(), name="kpi-testers-current-status"),
]