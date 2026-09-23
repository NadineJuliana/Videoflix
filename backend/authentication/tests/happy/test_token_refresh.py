"""
Happy path tests for token refresh.
"""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class TokenRefreshHappyPathTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="securepassword",
            is_active=True,
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.client.cookies["refresh_token"] = str(self.refresh)

    def test_token_refresh_returns_status_200(self):
        response = self.client.post(
            "/api/token/refresh/",
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_token_refresh_returns_new_access_token(self):
        response = self.client.post(
            "/api/token/refresh/",
            format="json",
        )

        self.assertEqual(
            response.data["detail"],
            "Token refreshed",
        )
        self.assertIn(
            "access",
            response.data,
        )
        self.assertTrue(
            response.data["access"],
        )

    def test_token_refresh_sets_access_token_cookie(self):
        response = self.client.post(
            "/api/token/refresh/",
            format="json",
        )

        self.assertIn(
            "access_token",
            response.cookies,
        )
        self.assertEqual(
            response.cookies["access_token"].value,
            response.data["access"],
        )
        self.assertTrue(
            response.cookies["access_token"]["httponly"],
        )
