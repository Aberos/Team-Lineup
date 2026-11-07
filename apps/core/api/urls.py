"""URL patterns for the core app."""

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
    path(
        f"{_BASE_AUTH}/login/",
        CoreLoginView.as_view(),
        name="core-auth-login",
    ),
    path(
        f"{_BASE_AUTH}/validate-token/",
        CoreValidateTokenView.as_view(),
        name="core-auth-validate-token",
    ),
    path(
        f"{_BASE_AUTH}/me/",
        CoreAuthenticatedUserInfoView.as_view(),
        name="core-auth-me",
    ),
    path(
        f"{_BASE_AUTH}/change-password/",
        CoreAuthenticatedUserChangePasswordView.as_view(),
        name="core-auth-change-password",
    ),
    path(
        f"{_BASE_AUTH}/change-name/",
        CoreAuthenticatedUserChangeNameView.as_view(),
        name="core-auth-change-name",
    ),
]
