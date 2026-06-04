"""Core service."""

from typing import Any

from django.contrib.auth import authenticate
from django.contrib.auth.models import AbstractBaseUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken


class CoreService:
    @staticmethod
    def login(username: str, password: str) -> Any:
        """Login user and return access token."""

        user = authenticate(username=username, password=password)
        if user is None:
            return None

        refresh = RefreshToken.for_user(user)
        return {"user": user, "token": str(refresh.access_token)}

    @staticmethod
    def validate_token(token: str) -> bool:
        """Validate token."""
        try:
            UntypedToken(token)
            return True
        except (InvalidToken, TokenError):
            return False

    @staticmethod
    def change_password(
        user: AbstractBaseUser,
        current_password: str,
        new_password: str,
    ) -> bool:
        """Change the authenticated user password."""
        if not user.check_password(current_password):
            return False

        user.set_password(new_password)
        user.save(update_fields=["password"])
        return True

    @staticmethod
    def change_name(
        user: AbstractBaseUser,
        first_name: str,
        last_name: str,
    ) -> bool:
        """Change the authenticated user name."""
        user.first_name = first_name
        user.last_name = last_name
        user.save(update_fields=["first_name", "last_name"])
        return True
