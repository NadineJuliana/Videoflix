"""
API views for user authentication.
"""


from django.contrib.auth import get_user_model
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
from authentication.utils import get_user_from_uid

User = get_user_model()


class RegisterView(APIView):
    """Register new users and send account activation emails."""

    def post(self, request):
        """Create an inactive user and send an activation email."""

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
    """Activate user accounts through activation links."""

    def get(self, _request, uidb64, token):
        """Activate the user when the activation token is valid."""

        user = get_user_from_uid(uidb64)

        if not user or not default_token_generator.check_token(user, token):
            return self.activation_failed()

        user.is_active = True
        user.save()

        return Response(
            {"message": "Account successfully activated."},
            status=status.HTTP_200_OK,
        )

    def activation_failed(self):
        """Return the response for an invalid activation request."""

        return Response(
            {"message": "Account activation failed."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginView(APIView):
    """Authenticate users and issue JWT cookies."""

    def post(self, request):
        """Authenticate the user and return JWT cookies."""

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        response = self.create_response(user)
        self.set_auth_cookies(response, refresh)
        return response

    def create_response(self, user):
        """Create the successful login response."""

        return Response(
            {
                "detail": "Login successful",
                "user": {
                    "id": user.id,
                    "username": user.username,
                },
            },
            status=status.HTTP_200_OK,
        )

    def set_auth_cookies(self, response, refresh):
        """Store access and refresh tokens in HTTP-only cookies."""

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


class LogoutView(APIView):
    """Log users out and invalidate their refresh tokens."""

    def post(self, request):
        """Blacklist the refresh token and remove authentication cookies."""

        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return self.missing_token_response()

        RefreshToken(refresh_token).blacklist()
        response = self.logout_response()
        self.delete_auth_cookies(response)
        return response

    def missing_token_response(self):
        """Return an error response when no refresh token is available."""

        return Response(
            {"detail": "Refresh token is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def logout_response(self):
        """Create the successful logout response."""

        return Response(
            {
                "detail": (
                    "Logout successful! All tokens will be deleted. "
                    "Refresh token is now invalid."
                )
            },
            status=status.HTTP_200_OK,
        )

    def delete_auth_cookies(self, response):
        """Remove authentication cookies from the response."""

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")


class TokenRefreshView(APIView):
    """Issue new access tokens from valid refresh tokens."""

    def post(self, request):
        """Refresh the access token stored in the authentication cookie."""

        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return self.missing_token_response()

        refresh = self.get_refresh_token(refresh_token)
        if not refresh:
            return self.invalid_token_response()

        access_token = str(refresh.access_token)
        response = self.create_response(access_token)
        self.set_access_cookie(response, access_token)
        return response

    def get_refresh_token(self, refresh_token):
        """Return a validated refresh token or None when invalid."""

        try:
            return RefreshToken(refresh_token)
        except TokenError:
            return None

    def missing_token_response(self):
        """Return an error response when no refresh token is available."""

        return Response(
            {"detail": "Refresh token is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def invalid_token_response(self):
        """Return an error response for an invalid refresh token."""

        return Response(
            {"detail": "Refresh token is invalid."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    def create_response(self, access_token):
        """Create the successful token refresh response."""

        return Response(
            {
                "detail": "Token refreshed",
                "access": access_token,
            },
            status=status.HTTP_200_OK,
        )

    def set_access_cookie(self, response, access_token):
        """Store the refreshed access token in an HTTP-only cookie."""

        response.set_cookie(
            "access_token",
            access_token,
            httponly=True,
        )


class PasswordResetView(APIView):
    """Handle password reset requests."""

    def post(self, request):
        """Send a password reset email when the account exists."""

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
    """Confirm password resets using UID and token."""

    def post(self, request, uidb64, token):
        """Set a new password when the reset token is valid."""

        serializer = PasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_user_from_uid(uidb64)

        if not user or not default_token_generator.check_token(user, token):
            return self.invalid_token_response()

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response(
            {"detail": "Your Password has been successfully reset."},
            status=status.HTTP_200_OK,
        )

    def invalid_token_response(self):
        """Return an error response for an invalid reset token."""

        return Response(
            {"detail": "Invalid or expired token."},
            status=status.HTTP_400_BAD_REQUEST,
        )
