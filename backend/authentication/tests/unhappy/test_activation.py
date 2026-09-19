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
    def test_activate_fails_with_invalid_token(self):
        user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="securepassword",
            is_active=False,
        )

        uid = urlsafe_base64_encode(force_bytes(user.pk))

        response = self.client.get(
            f"/api/activate/{uid}/invalid-token/"
        )

        user.refresh_from_db()

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertFalse(user.is_active)

    def test_activate_fails_with_invalid_uid(self):
        user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="securepassword",
            is_active=False,
        )

        token = default_token_generator.make_token(user)

        response = self.client.get(
            f"/api/activate/invalid-uid/{token}/"
        )

        user.refresh_from_db()

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertFalse(user.is_active)
