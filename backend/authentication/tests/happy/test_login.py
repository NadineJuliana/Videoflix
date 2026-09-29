"""
Happy path tests for user login.
"""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class LoginHappyPathTest(APITestCase):
    """Test successful user login."""

    def setUp(self):
        """Create an active user and valid login credentials."""

        self.user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="securepassword",
            is_active=True,
        )
        self.data = {
            "email": self.user.email,
            "password": "securepassword",
        }

    def test_login_returns_status_200(self):
        """Return HTTP 200 for valid login credentials."""

        response = self.client.post(
            "/api/login/",
            self.data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_returns_user_data(self):
        """Return the authenticated user's data."""

        response = self.client.post(
            "/api/login/",
            self.data,
            format="json",
        )

        self.assertEqual(
            response.data,
            {
                "detail": "Login successful",
                "user": {
                    "id": self.user.id,
                    "username": self.user.username,
                },
            },
        )

    def test_login_sets_http_only_token_cookies(self):
        """Store access and refresh tokens in HTTP-only cookies."""

        response = self.client.post(
            "/api/login/",
            self.data,
            format="json",
        )

        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)
        self.assertTrue(response.cookies["access_token"]["httponly"])
        self.assertTrue(response.cookies["refresh_token"]["httponly"])
