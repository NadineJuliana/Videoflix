"""
Email services for authentication workflows.
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_activation_email(user, token):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    activation_link = f"/api/activate/{uid}/{token}/"

    html_message = render_to_string(
        "authentication/activation_email.html",
        {"activation_link": activation_link,
         "username": user.username,
         },

    )

    send_mail(
        subject="Confirm your email",
        message=f"Activate your account: {activation_link}",
        from_email=None,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_password_reset_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    reset_link = f"/api/password_confirm/{uid}/{token}/"

    html_message = render_to_string(
        "authentication/password_reset_email.html",
        {
            "reset_link": reset_link,
        },
    )

    send_mail(
        subject="Reset your Password",
        message=(
            "Reset your password using the following link:\n"
            f"{reset_link}"
        ),
        from_email=None,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )
