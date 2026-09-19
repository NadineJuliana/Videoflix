"""
Email services for authentication workflows.
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_activation_email(user, token):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    activation_link = f"/api/activate/{uid}/{token}/"

    html_message = render_to_string(
        "authentication/activation_email.html",
        {"activation_link": activation_link, },

    )

    send_mail(
        subject="Confirm your email",
        message=f"Activate your account: {activation_link}",
        from_email=None,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )
