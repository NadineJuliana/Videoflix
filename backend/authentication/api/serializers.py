"""
Serializers for authentication API endpoints.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework import serializers


User = get_user_model()


class RegistrationSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirmed_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Unable to register with this email."
            )

        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["confirmed_password"]:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."}
            )

        return attrs

    def create(self, validated_data):
        email = validated_data["email"]
        password = validated_data["password"]

        return User.objects.create_user(
            username=email,
            email=email,
            password=password,
            is_active=False,
        )


class LoginSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            username=attrs["email"],
            password=attrs["password"],
        )

        if not user:
            raise serializers.ValidationError(
                "Invalid email or password."
            )

        attrs["user"] = user
        return attrs


class PasswordResetSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    email = serializers.EmailField()


class PasswordConfirmSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"new_password": "Passwords do not match."}
            )

        return attrs
