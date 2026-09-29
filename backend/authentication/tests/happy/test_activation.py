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
    """Test successful user account activation."""

    def setUp(self):
        """Create an inactive user and valid activation credentials."""

        self.user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="securepassword",
            is_active=False,
        )
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)
        self.url = f"/api/activate/{self.uid}/{self.token}/"

    def test_activate_returns_status_200(self):
        """Return HTTP 200 for a valid activation request."""

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_activate_sets_user_active(self):
        """Activate the user after a valid activation request."""

        self.client.get(self.url)
        self.user.refresh_from_db()

        self.assertTrue(self.user.is_active)

    def test_activate_returns_success_message(self):
        """Return the expected message after successful activation."""

        response = self.client.get(self.url)

        self.assertEqual(
            response.data,
            {"message": "Account successfully activated."},
        )
