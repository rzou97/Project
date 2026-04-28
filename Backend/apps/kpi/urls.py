from django.urls import path

from apps.kpi.api.views import (
    CurrentFailureRateView,
    TestersCurrentStatusView,
    TestersFpyInstantView,
)

urlpatterns = [
    path("testers-fpy-instant/", TestersFpyInstantView.as_view(), name="kpi-testers-fpy-instant"),
    path("testers-current-status/", TestersCurrentStatusView.as_view(), name="kpi-testers-current-status"),
    path("current-failure-rate/", CurrentFailureRateView.as_view(), name="kpi-current-failure-rate"),
]
