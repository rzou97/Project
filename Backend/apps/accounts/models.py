from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        PROD_MANAGER = "PROD_MANAGER", "Prod Manager"
        QUALITY_MANAGER = "QUALITY_MANAGER", "Quality Manager"
        REPAIR_TECHNICIAN = "REPAIR_TECHNICIAN", "Repair Technician"
        TEST_MANAGER = "TEST_MANAGER", "Test Manager"

    username = None
    email = models.EmailField(unique=True)

    # Mapping métier :
    # first_name = prénom
    # last_name = nom
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    matricule = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=30, choices=Role.choices)
    email_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "matricule", "role"]

    class Meta:
        db_table = "accounts_user"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} - {self.matricule}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()