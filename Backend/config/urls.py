"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.accounts.api.views import CustomTokenObtainPairView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/auth/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("api/accounts/", include("apps.accounts.urls")),
    path("api/boards/", include("apps.boards.urls")),
    path("api/test-results/", include("apps.testresults.urls")),
    path("api/failure-cases/", include("apps.failures.urls")),
    path("api/repairs/", include("apps.repairs.urls")),
    path("api/pdr/", include("apps.pdr.urls")),
    path("api/maintenance/", include("apps.maintenance.urls")),
    path("api/alerts/", include("apps.alerts.urls")),
    path("api/calibration/", include("apps.calibration.urls")),
    path("api/intelligence/", include("apps.intelligence.urls")),
    path("api/kpi/", include("apps.kpi.urls")),
    path("api/sync-engine/", include("apps.syncengine.urls")),
]
