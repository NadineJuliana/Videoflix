"""
URL configuration for authentication API endpoints.
"""

from django.urls import path

from authentication.api.views import ActivateView, RegisterView


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path(
        "activate/<uidb64>/<token>/",
        ActivateView.as_view(),
        name="activate",
    ),
]
