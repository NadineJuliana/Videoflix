"""
Email services for authentication workflows.
"""

from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_activation_email(user, token):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    activation_link = f"/api/activate/{uid}/{token}/"

    send_mail(
        subject="Activate your Videoflix account",
        message=f"Please click the following link to activate your account: {activation_link}",
        from_email=None,
        recipient_list=[user.email],
        fail_silently=False,
    )
