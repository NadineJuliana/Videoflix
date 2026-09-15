from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


User = get_user_model()


class RegisterHappyPathTest(APITestCase):
    def test_register_user_successfully(self):
        data = {
            "email": "user@example.com",
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
            status.HTTP_201_CREATED,
        )

    def test_register_creates_user(self):
        data = {
            "email": "user@example.com",
            "password": "securepassword",
            "confirmed_password": "securepassword",
        }

        self.client.post(
            "/api/register/",
            data,
            format="json",
        )

        self.assertTrue(
            User.objects.filter(
                email="user@example.com",
            ).exists()
        )

    def test_registered_user_is_inactive(self):
        data = {
            "email": "user@example.com",
            "password": "securepassword",
            "confirmed_password": "securepassword",
        }

        self.client.post(
            "/api/register/",
            data,
            format="json",
        )

        user = User.objects.get(email="user@example.com")

        self.assertFalse(user.is_active)

    def test_register_returns_user_data(self):
        data = {
            "email": "user@example.com",
            "password": "securepassword",
            "confirmed_password": "securepassword",
        }

        response = self.client.post(
            "/api/register/",
            data,
            format="json",
        )

        user = User.objects.get(email="user@example.com")

        self.assertEqual(
            response.data["user"],
            {
                "id": user.id,
                "email": user.email,
            },
        )

    def test_register_returns_activation_token(self):
        data = {
            "email": "user@example.com",
            "password": "securepassword",
            "confirmed_password": "securepassword",
        }

        response = self.client.post(
            "/api/register/",
            data,
            format="json",
        )

        self.assertIn("token", response.data)
        self.assertTrue(response.data["token"])

    def test_registration_sends_activation_email(self):
        data = {
            "email": "user@example.com",
            "password": "securepassword",
            "confirmed_password": "securepassword",
        }

        self.client.post(
            "/api/register/",
            data,
            format="json",
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].to,
            ["user@example.com"],
        )

    def test_activation_email_contains_activation_link(self):
        data = {
            "email": "user@example.com",
            "password": "securepassword",
            "confirmed_password": "securepassword",
        }

        response = self.client.post(
            "/api/register/",
            data,
            format="json",
        )

        user = User.objects.get(email="user@example.com")
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = response.data["token"]

        expected_link = f"/api/activate/{uid}/{token}/"

        self.assertIn(
            expected_link,
            mail.outbox[0].body,
        )
