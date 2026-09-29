"""
Happy path tests for user logout.
"""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class LogoutHappyPathTest(APITestCase):
    """Test successful user logout."""

    def setUp(self):
        """Create an authenticated user with valid JWT cookies."""

        self.user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="securepassword",
            is_active=True,
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.client.cookies["access_token"] = str(self.refresh.access_token)
        self.client.cookies["refresh_token"] = str(self.refresh)

    def test_logout_returns_status_200(self):
        """Return HTTP 200 after successful logout."""

        response = self.client.post(
            "/api/logout/",
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_logout_returns_success_message(self):
        """Return the expected message after successful logout."""

        response = self.client.post(
            "/api/logout/",
            format="json",
        )

        self.assertEqual(
            response.data,
            {
                "detail": (
                    "Logout successful! All tokens will be deleted. "
                    "Refresh token is now invalid."
                )
            },
        )

    def test_logout_deletes_token_cookies(self):
        """Delete access and refresh token cookies."""

        response = self.client.post(
            "/api/logout/",
            format="json",
        )

        self.assertEqual(
            response.cookies["access_token"].value,
            "",
        )
        self.assertEqual(
            response.cookies["refresh_token"].value,
            "",
        )

    def test_logout_blacklists_refresh_token(self):
        """Blacklist the refresh token after logout."""

        self.client.post(
            "/api/logout/",
            format="json",
        )

        self.assertTrue(
            BlacklistedToken.objects.filter(  # pylint: disable=no-member
                token__jti=self.refresh["jti"]
            ).exists()
        )
