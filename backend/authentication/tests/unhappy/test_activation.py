"""
Unhappy path tests for user account activation.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class ActivationUnhappyPathTest(APITestCase):
    """Test failed user account activation attempts."""

    def setUp(self):
        """Create an inactive user with valid activation credentials."""

        self.user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="securepassword",
            is_active=False,
        )
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)

    def test_activate_fails_with_invalid_token(self):
        """Reject account activation with an invalid token."""

        response = self.client.get(
            f"/api/activate/{self.uid}/invalid-token/"
        )
        self.user.refresh_from_db()

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertFalse(self.user.is_active)

    def test_activate_fails_with_invalid_uid(self):
        """Reject account activation with an invalid UID."""

        response = self.client.get(
            f"/api/activate/invalid-uid/{self.token}/"
        )
        self.user.refresh_from_db()

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertFalse(self.user.is_active)
