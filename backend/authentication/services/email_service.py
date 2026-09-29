"""
Email services for authentication workflows.
"""

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def get_activation_link(user, token):
    """Create the activation link for a user."""

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    return f"/api/activate/{uid}/{token}/"


def send_activation_email(user, token):
    """Send an account activation email to the user."""

    activation_link = get_activation_link(user, token)
    html_message = render_to_string(
        "authentication/activation_email.html",
        {
            "activation_link": activation_link,
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


def get_password_reset_link(user):
    """Create a password reset link for a user."""

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return f"/api/password_confirm/{uid}/{token}/"


def send_password_reset_email(user):
    """Send a password reset email to the user."""

    reset_link = get_password_reset_link(user)
    html_message = render_to_string(
        "authentication/password_reset_email.html",
        {"reset_link": reset_link},
    )

    send_mail(
        subject="Reset your Password",
        message=f"Reset your password using this link:\n{reset_link}",
        from_email=None,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )
