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
from rest_framework_simplejwt.exceptions import TokenError

from authentication.api.serializers import (
    LoginSerializer,
    PasswordConfirmSerializer,
    PasswordResetSerializer,
    RegistrationSerializer,
)
from authentication.services.email_service import (
    send_activation_email,
    send_password_reset_email,
)

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
    def get(self, _request, uidb64, token):
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


class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        RefreshToken(refresh_token).blacklist()

        response = Response(
            {
                "detail": (
                    "Logout successful! All tokens will be deleted. "
                    "Refresh token is now invalid."
                )
            },
            status=status.HTTP_200_OK,
        )

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response


class TokenRefreshView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(refresh_token)
        except TokenError:
            return Response(
                {"detail": "Refresh token is invalid."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_token = str(refresh.access_token)

        response = Response(
            {
                "detail": "Token refreshed",
                "access": access_token,
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            "access_token",
            access_token,
            httponly=True,
        )

        return response


class PasswordResetView(APIView):
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()

        if user:
            send_password_reset_email(user)

        return Response(
            {
                "detail": (
                    "An email has been sent to reset your password."
                )
            },
            status=status.HTTP_200_OK,
        )


class PasswordConfirmView(APIView):
    def post(self, request, uidb64, token):
        serializer = PasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.get_user(uidb64)

        if not user or not default_token_generator.check_token(user, token):
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(
            serializer.validated_data["new_password"]
        )
        user.save()

        return Response(
            {
                "detail": (
                    "Your Password has been successfully reset."
                )
            },
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
