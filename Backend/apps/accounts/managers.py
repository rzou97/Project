from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(
        self,
        email,
        password=None,
        first_name="",
        last_name="",
        matricule="",
        role="TEST_MANAGER",
        **extra_fields,
    ):
        if not email:
            raise ValueError("L'email est obligatoire.")
        if not matricule:
            raise ValueError("Le matricule est obligatoire.")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            matricule=matricule,
            role=role,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email,
        password,
        first_name="Admin",
        last_name="System",
        matricule="ADMIN001",
        role="ADMIN",
        **extra_fields,
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("email_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Le superuser doit avoir is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Le superuser doit avoir is_superuser=True.")

        return self.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            matricule=matricule,
            role=role,
            **extra_fields,
        )