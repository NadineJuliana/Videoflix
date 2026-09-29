"""
Happy path tests for password confirmation.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class PasswordConfirmHappyPathTest(APITestCase):
    """Test successful password confirmation."""

    def setUp(self):
        """Create a user with valid password reset credentials."""

        self.user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="securepassword",
            is_active=True,
        )
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        self.url = f"/api/password_confirm/{uid}/{token}/"
        self.data = {
            "new_password": "newsecurepassword",
            "confirm_password": "newsecurepassword",
        }

    def test_password_confirm_returns_status_200(self):
        """Return HTTP 200 for a valid password confirmation."""

        response = self.client.post(
            self.url,
            self.data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_confirm_updates_password(self):
        """Update the user's password."""

        self.client.post(self.url, self.data, format="json")
        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password("newsecurepassword")
        )

    def test_password_confirm_returns_success_message(self):
        """Return the expected message after resetting the password."""

        response = self.client.post(
            self.url,
            self.data,
            format="json",
        )

        self.assertEqual(
            response.data,
            {
                "detail": (
                    "Your Password has been successfully reset."
                )
            },
        )
