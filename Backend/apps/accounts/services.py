from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_verification_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    activation_path = reverse("accounts-activate", kwargs={"uidb64": uid, "token": token})
    backend_activation_url = f"http://127.0.0.1:8000{activation_path}"

    frontend_base_url = getattr(settings, "FRONTEND_BASE_URL", "http://localhost:4200").rstrip("/")
    frontend_activation_url = f"{frontend_base_url}/activation/{uid}/{token}"

    subject = "Confirmation de votre compte"
    message = (
        f"Bonjour {user.first_name},\n\n"
        f"Veuillez confirmer votre inscription en cliquant sur le lien suivant:\n"
        f"{frontend_activation_url}\n\n"
        f"Si ce lien ne fonctionne pas, utilisez ce lien direct API:\n"
        f"{backend_activation_url}\n\n"
        f"Si vous n etes pas a l origine de cette demande, ignorez ce message."
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        recipient_list=[user.email],
        fail_silently=False,
    )
