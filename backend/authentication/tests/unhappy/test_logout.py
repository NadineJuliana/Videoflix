"""
Unhappy path tests for user logout.
"""

from rest_framework import status
from rest_framework.test import APITestCase


class LogoutUnhappyPathTest(APITestCase):
    """Test failed user logout attempts."""

    def test_logout_without_refresh_token_returns_status_400(self):
        """Return HTTP 400 when the refresh token is missing."""

        response = self.client.post(
            "/api/logout/",
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
