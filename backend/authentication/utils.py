"""
Utility functions for authentication workflows.
"""

from django.contrib.auth import get_user_model
from django.utils.encoding import DjangoUnicodeDecodeError, force_str
from django.utils.http import urlsafe_base64_decode


User = get_user_model()


def get_user_from_uid(uidb64):
    """Return the user encoded by the given UID or None if invalid."""

    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        return User.objects.get(pk=user_id)
    except (
        ValueError,
        TypeError,
        OverflowError,
        DjangoUnicodeDecodeError,
        User.DoesNotExist,
    ):
        return None
