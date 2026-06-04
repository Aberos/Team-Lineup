"""Auth API routes."""

from django.urls import path

from apps.core.api.views import (
    CoreAuthenticatedUserChangeNameView,
    CoreAuthenticatedUserChangePasswordView,
    CoreAuthenticatedUserInfoView,
    CoreLoginView,
    CoreValidateTokenView,
)

_BASE_AUTH = "auth"

urlpatterns = [
    path(f"{_BASE_AUTH}/login/", CoreLoginView.as_view(), name="auth-login"),
    path(
        f"{_BASE_AUTH}/validate-token/",
        CoreValidateTokenView.as_view(),
        name="auth-validate",
    ),
    path(
        f"{_BASE_AUTH}/me/",
        CoreAuthenticatedUserInfoView.as_view(),
        name="auth-me",
    ),
    path(
        f"{_BASE_AUTH}/change-password",
        CoreAuthenticatedUserChangePasswordView.as_view(),
        name="auth-change-password",
    ),
    path(
        f"{_BASE_AUTH}/change-name",
        CoreAuthenticatedUserChangeNameView.as_view(),
        name="auth-change-name",
    ),
]
