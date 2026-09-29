"""
Happy path tests for user registration.
"""

from django.contrib.auth import get_user_model
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class RegisterHappyPathTest(APITestCase):
    """Test successful user registration."""

    def setUp(self):
        """Prepare valid registration data."""

        self.data = {
            "email": "user@example.com",
            "password": "securepassword",
            "confirmed_password": "securepassword",
        }

    def test_register_user_successfully(self):
        """Return HTTP 201 for valid registration data."""

        response = self.client.post(
            "/api/register/",
            self.data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_creates_user(self):
        """Create a user with the submitted email address."""

        self.client.post("/api/register/", self.data, format="json")

        self.assertTrue(
            User.objects.filter(  # pylint: disable=no-member
                email=self.data["email"]
            ).exists()
        )

    def test_registered_user_is_inactive(self):
        """Create registered users as inactive."""

        self.client.post("/api/register/", self.data, format="json")
        user = User.objects.get(email=self.data["email"])

        self.assertFalse(user.is_active)

    def test_register_returns_user_data(self):
        """Return the created user's ID and email address."""

        response = self.client.post(
            "/api/register/",
            self.data,
            format="json",
        )
        user = User.objects.get(email=self.data["email"])

        self.assertEqual(
            response.data["user"],
            {"id": user.id, "email": user.email},
        )

    def test_register_returns_activation_token(self):
        """Return an activation token after registration."""

        response = self.client.post(
            "/api/register/",
            self.data,
            format="json",
        )

        self.assertIn("token", response.data)
        self.assertTrue(response.data["token"])

    def test_registration_sends_activation_email(self):
        """Send one activation email to the registered user."""

        self.client.post("/api/register/", self.data, format="json")

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.data["email"]])

    def test_activation_email_contains_activation_link(self):
        """Include the frontend account activation URL in the email."""

        response = self.client.post(
            "/api/register/",
            self.data,
            format="json",
        )
        user = User.objects.get(email=self.data["email"])
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = response.data["token"]

        self.assertIn(
            (
                "http://127.0.0.1:5500/pages/auth/activate.html"
                f"?uid={uid}&token={token}"
            ),
            mail.outbox[0].body,
        )

    def test_activation_email_contains_html_content(self):
        """Include an HTML alternative in the activation email."""

        self.client.post("/api/register/", self.data, format="json")

        self.assertEqual(len(mail.outbox[0].alternatives), 1)
