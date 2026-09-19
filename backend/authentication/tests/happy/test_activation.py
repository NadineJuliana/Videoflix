"""
Happy path tests for user account activation.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class ActivationHappyPathTest(APITestCase):
    def test_activate_returns_status_200(self):
        user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="securepassword",
            is_active=False,
        )

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        response = self.client.get(
            f"/api/activate/{uid}/{token}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_activate_sets_user_active(self):
        user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="securepassword",
            is_active=False,
        )

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        self.client.get(
            f"/api/activate/{uid}/{token}/"
        )

        user.refresh_from_db()

        self.assertTrue(user.is_active)

    def test_activate_returns_success_message(self):
        user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="securepassword",
            is_active=False,
        )

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        response = self.client.get(
            f"/api/activate/{uid}/{token}/"
        )

        self.assertEqual(
            response.data,
            {"message": "Account successfully activated."},
        )
