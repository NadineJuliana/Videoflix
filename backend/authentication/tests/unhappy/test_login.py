"""
Unhappy path tests for user login.
"""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class LoginUnhappyPathTest(APITestCase):
    def test_login_with_invalid_credentials_fails(self):
        User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="securepassword",
            is_active=True,
        )

        data = {
            "email": "user@example.com",
            "password": "wrongpassword",
        }

        response = self.client.post(
            "/api/login/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_login_with_inactive_user_fails(self):
        User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="securepassword",
            is_active=False,
        )

        data = {
            "email": "user@example.com",
            "password": "securepassword",
        }

        response = self.client.post(
            "/api/login/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
