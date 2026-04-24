from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.accounts.services import send_verification_email

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "matricule",
            "role",
            "password",
            "confirm_password",
        )
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate_email(self, value):
        email = value.strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "Un compte avec cet email existe déjà."
            )

        if "@" not in email:
            raise serializers.ValidationError("Adresse email invalide.")

        domain = email.split("@", 1)[1].lower()

        allowed_domains = getattr(
            settings,
            "ALLOWED_REGISTRATION_EMAIL_DOMAINS",
            ["atems.tn"],
        )

        allowed_domains = [d.strip().lower() for d in allowed_domains if d.strip()]

        if domain not in allowed_domains:
            raise serializers.ValidationError(
                f"Seules les adresses email du domaine suivant sont autorisées : {', '.join(allowed_domains)}"
            )

        return email

    def validate_matricule(self, value):
        matricule = value.strip()

        if User.objects.filter(matricule__iexact=matricule).exists():
            raise serializers.ValidationError("Ce matricule existe déjà.")

        return matricule

    def validate_role(self, value):
        if value == User.Role.ADMIN:
            raise serializers.ValidationError(
                "Le rôle ADMIN ne peut pas être attribué via l'inscription publique."
            )
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError(
                {
                    "confirm_password": (
                        "La confirmation du mot de passe ne correspond pas."
                    )
                }
            )

        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"].strip(),
            last_name=validated_data["last_name"].strip(),
            matricule=validated_data["matricule"],
            role=validated_data["role"],
            is_active=True,
            email_verified=False,
        )

        send_verification_email(user)
        return user


class MeSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "matricule",
            "role",
            "email_verified",
            "is_active",
            "created_at",
        )


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["role"] = user.role
        token["matricule"] = user.matricule
        token["full_name"] = user.full_name
        token["email_verified"] = user.email_verified
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.email_verified:
            raise serializers.ValidationError(
                "Veuillez confirmer votre adresse email avant de vous connecter."
            )

        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "full_name": self.user.full_name,
            "matricule": self.user.matricule,
            "role": self.user.role,
            "email_verified": self.user.email_verified,
        }
        return data