"""Auth API routes."""

from django.urls import path

from apps.core.api.views import CoreLoginView

_BASE_AUTH = "auth"

urlpatterns = [
    path(f"{_BASE_AUTH}/login/", CoreLoginView.as_view(), name="auth-login"),
]
