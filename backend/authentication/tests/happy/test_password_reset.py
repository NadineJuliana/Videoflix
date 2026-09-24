"""
Happy path tests for password reset.
"""

from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APITestCase


User = get_user_model()


class PasswordResetHappyPathTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="securepassword",
            is_active=True,
        )

    def test_password_reset_returns_status_200(self):
        response = self.client.post(
            "/api/password_reset/",
            {
                "email": self.user.email,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_password_reset_returns_success_message(self):
        response = self.client.post(
            "/api/password_reset/",
            {
                "email": self.user.email,
            },
            format="json",
        )

        self.assertEqual(
            response.data,
            {
                "detail": "An email has been sent to reset your password."
            },
        )

    def test_password_reset_sends_email(self):
        self.client.post(
            "/api/password_reset/",
            {
                "email": self.user.email,
            },
            format="json",
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )
        self.assertEqual(
            mail.outbox[0].to,
            [self.user.email],
        )

    def test_password_reset_email_contains_reset_link(self):
        self.client.post(
            "/api/password_reset/",
            {
                "email": self.user.email,
            },
            format="json",
        )

        uid = urlsafe_base64_encode(force_bytes(self.user.pk))

        self.assertIn(
            f"/api/password_confirm/{uid}/",
            mail.outbox[0].body,
        )

    def test_password_reset_email_has_html_alternative(self):
        self.client.post(
            "/api/password_reset/",
            {"email": self.user.email},
            format="json",
        )

        self.assertEqual(
            mail.outbox[0].alternatives[0].mimetype,
            "text/html",
        )
