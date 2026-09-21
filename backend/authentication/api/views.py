"""
API views for user authentication.
"""

from django.contrib.auth import get_user_model
from django.utils.encoding import DjangoUnicodeDecodeError, force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.api.serializers import (
    LoginSerializer,
    RegistrationSerializer,
)
from authentication.services.email_service import send_activation_email

User = get_user_model()


class RegisterView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = default_token_generator.make_token(user)
        send_activation_email(user, token)

        return Response(
            {
                "user": {
                    "id": user.id,
                    "email": user.email,
                },
                "token": token,
            },
            status=status.HTTP_201_CREATED,
        )


class ActivateView(APIView):
    def get(self, request, uidb64, token):
        user = self.get_user(uidb64)

        if not user or not default_token_generator.check_token(user, token):
            return self.activation_failed()

        user.is_active = True
        user.save()

        return Response(
            {"message": "Account successfully activated."},
            status=status.HTTP_200_OK,
        )

    def get_user(self, uidb64):
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            return User.objects.get(pk=user_id)
        except (
            ValueError,
            TypeError,
            OverflowError,
            DjangoUnicodeDecodeError,
            User.DoesNotExist,
        ):
            return None

    def activation_failed(self):
        return Response(
            {"message": "Account activation failed."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        response = Response(
            {
                "detail": "Login successful",
                "user": {
                    "id": user.id,
                    "username": user.username,
                },
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            "access_token",
            str(refresh.access_token),
            httponly=True,
        )
        response.set_cookie(
            "refresh_token",
            str(refresh),
            httponly=True,
        )

        return response
