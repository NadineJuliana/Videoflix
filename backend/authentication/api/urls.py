"""
URL configuration for authentication API endpoints.
"""

from django.urls import path

from authentication.api.views import RegisterView


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
]
