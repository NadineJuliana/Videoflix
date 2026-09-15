"""
Serializers for authentication API endpoints.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirmed_password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        email = validated_data["email"]
        password = validated_data["password"]

        return User.objects.create_user(
            username=email,
            email=email,
            password=password,
            is_active=False,
        )
