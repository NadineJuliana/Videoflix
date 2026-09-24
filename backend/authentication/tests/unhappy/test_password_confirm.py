"""
Unhappy path tests for password confirmation.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class PasswordConfirmUnhappyPathTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="securepassword",
            is_active=True,
        )

        self.uid = urlsafe_base64_encode(
            force_bytes(self.user.pk)
        )
        self.token = default_token_generator.make_token(
            self.user
        )

    def test_password_confirm_with_mismatching_passwords_returns_status_400(self):
        response = self.client.post(
            f"/api/password_confirm/{self.uid}/{self.token}/",
            {
                "new_password": "newsecurepassword",
                "confirm_password": "differentpassword",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_password_confirm_with_invalid_token_returns_status_400(self):
        response = self.client.post(
            f"/api/password_confirm/{self.uid}/invalid-token/",
            {
                "new_password": "newsecurepassword",
                "confirm_password": "newsecurepassword",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_password_confirm_with_invalid_uid_returns_status_400(self):
        response = self.client.post(
            f"/api/password_confirm/invalid-uid/{self.token}/",
            {
                "new_password": "newsecurepassword",
                "confirm_password": "newsecurepassword",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
