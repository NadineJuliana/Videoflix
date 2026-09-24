"""
Unhappy path tests for password reset.
"""

from django.core import mail
from rest_framework import status
from rest_framework.test import APITestCase


class PasswordResetUnhappyPathTest(APITestCase):
    def test_password_reset_with_unknown_email_sends_no_email(self):
        response = self.client.post(
            "/api/password_reset/",
            {
                "email": "unknown@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            len(mail.outbox),
            0,
        )

    def test_password_reset_without_email_returns_status_400(self):
        response = self.client.post(
            "/api/password_reset/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
