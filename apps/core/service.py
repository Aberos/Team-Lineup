"""Core service."""

from typing import Any

from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class CoreService:
    @staticmethod
    def login(username: str, password: str) -> Any:
        """Login user and return access token."""

        user = authenticate(username=username, password=password)
        if user is None:
            return None

        refresh = RefreshToken.for_user(user)
        return {"user": user, "token": str(refresh.access_token)}
