from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User

    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "matricule",
        "role",
        "email_verified",
        "is_active",
        "is_staff",
    )
    list_filter = ("role", "email_verified", "is_active", "is_staff", "is_superuser")
    search_fields = ("email", "first_name", "last_name", "matricule")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Informations personnelles", {"fields": ("first_name", "last_name", "matricule", "role")}),
        ("Vérification", {"fields": ("email_verified",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates importantes", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "matricule",
                    "role",
                    "password1",
                    "password2",
                    "email_verified",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )