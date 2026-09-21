"""
Happy path tests for user login.
"""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class LoginHappyPathTest(APITestCase):
    def test_login_returns_status_200(self):
        User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="securepassword",
            is_active=True,
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
            status.HTTP_200_OK,
        )

    def test_login_returns_user_data(self):
        user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="securepassword",
            is_active=True,
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
            response.data,
            {
                "detail": "Login successful",
                "user": {
                    "id": user.id,
                    "username": "user@example.com",
                },
            },
        )

    def test_login_sets_http_only_token_cookies(self):
        User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="securepassword",
            is_active=True,
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

        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

        self.assertTrue(
            response.cookies["access_token"]["httponly"]
        )
        self.assertTrue(
            response.cookies["refresh_token"]["httponly"]
        )
