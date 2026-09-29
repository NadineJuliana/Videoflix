"""
Unhappy path tests for user registration.
"""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class RegisterUnhappyPathTest(APITestCase):
    """Test failed user registration attempts."""

    def test_register_fails_when_passwords_do_not_match(self):
        """Reject registration when password confirmation differs."""

        data = {
            "email": "user@example.com",
            "password": "securepassword",
            "confirmed_password": "differentpassword",
        }

        response = self.client.post(
            "/api/register/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertFalse(
            User.objects.filter(email=data["email"]).exists()
        )

    def test_register_fails_when_email_already_exists(self):
        """Reject registration when the email is already registered."""

        User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="securepassword",
        )
        data = {
            "email": "user@example.com",
            "password": "newsecurepassword",
            "confirmed_password": "newsecurepassword",
        }

        response = self.client.post(
            "/api/register/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            User.objects.filter(email=data["email"]).count(),
            1,
        )

    def test_register_fails_with_invalid_email(self):
        """Reject registration with an invalid email address."""

        data = {
            "email": "invalid-email",
            "password": "securepassword",
            "confirmed_password": "securepassword",
        }

        response = self.client.post(
            "/api/register/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertFalse(
            User.objects.filter(email=data["email"]).exists()
        )

    def test_register_fails_when_required_field_is_missing(self):
        """Reject registration when any required field is missing."""

        valid_data = {
            "email": "user@example.com",
            "password": "securepassword",
            "confirmed_password": "securepassword",
        }

        for field in valid_data:
            with self.subTest(field=field):
                data = valid_data.copy()
                data.pop(field)
                response = self.client.post(
                    "/api/register/",
                    data,
                    format="json",
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_400_BAD_REQUEST,
                )
                self.assertFalse(
                    User.objects.filter(
                        email="user@example.com"
                    ).exists()
                )
