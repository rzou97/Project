from django.urls import path

from apps.accounts.api.views import (
    ActivateAccountView,
    MeView,
    RegisterView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="accounts-register"),
    path("me/", MeView.as_view(), name="accounts-me"),
    path(
        "activate/<uidb64>/<token>/",
        ActivateAccountView.as_view(),
        name="accounts-activate",
    ),
]