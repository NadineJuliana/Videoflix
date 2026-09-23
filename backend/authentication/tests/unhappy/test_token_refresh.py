"""
Unhappy path tests for token refresh.
"""

from rest_framework import status
from rest_framework.test import APITestCase


class TokenRefreshUnhappyPathTest(APITestCase):
    def test_token_refresh_without_refresh_token_returns_status_400(self):
        response = self.client.post(
            "/api/token/refresh/",
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_token_refresh_with_invalid_refresh_token_returns_status_401(self):
        self.client.cookies["refresh_token"] = "invalid-refresh-token"

        response = self.client.post(
            "/api/token/refresh/",
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
