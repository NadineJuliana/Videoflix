"""
Happy path tests for password reset.
"""

from django.contrib.auth import get_user_model
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class PasswordResetHappyPathTest(APITestCase):
    """Test successful password reset requests."""

    def setUp(self):
        """Create an active user for password reset requests."""

        self.user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="securepassword",
            is_active=True,
        )
        self.data = {"email": self.user.email}

    def test_password_reset_returns_status_200(self):
        """Return HTTP 200 for a valid password reset request."""

        response = self.client.post(
            "/api/password_reset/",
            self.data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_returns_success_message(self):
        """Return the expected password reset message."""

        response = self.client.post(
            "/api/password_reset/",
            self.data,
            format="json",
        )

        self.assertEqual(
            response.data,
            {"detail": "An email has been sent to reset your password."},
        )

    def test_password_reset_sends_email(self):
        """Send one password reset email to the user."""
        self.client.post(
            "/api/password_reset/",
            self.data,
            format="json",
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])

    def test_password_reset_email_contains_reset_link(self):
        """Include the frontend password reset URL in the reset email."""

        self.client.post(
            "/api/password_reset/",
            self.data,
            format="json",
        )
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))

        self.assertIn(
            (
                "http://127.0.0.1:5500/pages/auth/confirm_password.html"
                f"?uid={uid}&token="
            ),
            mail.outbox[0].body,
        )

    def test_password_reset_email_has_html_alternative(self):
        """Include an HTML alternative in the password reset email."""

        self.client.post(
            "/api/password_reset/",
            self.data,
            format="json",
        )

        self.assertEqual(
            mail.outbox[0].alternatives[0].mimetype,
            "text/html",
        )
