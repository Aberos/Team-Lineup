"""Services for authentication and authenticated user data."""

from dataclasses import dataclass

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.exceptions import InvalidCredentialsError
from apps.core.repository import UserRepository


@dataclass(frozen=True)
class LoginTokens:
    """Tokens issued by a successful login.

    Attributes:
        access: Short-lived JWT used in the Authorization header.
        refresh: Long-lived JWT used to obtain new access tokens.
    """

    access: str
    refresh: str


class CoreService:
    """Business rules for authentication and user data."""

    @staticmethod
    def login(username: str, password: str) -> LoginTokens:
        """Authenticate the user and issue access and refresh tokens.

        Args:
            username: Username of the account.
            password: Password of the account.

        Returns:
            The encoded JWT access and refresh tokens.

        Raises:
            InvalidCredentialsError: If the credentials are invalid or the
                user is inactive.
        """
        user = authenticate(username=username, password=password)
        if user is None:
            raise InvalidCredentialsError
        refresh = RefreshToken.for_user(user)
        return LoginTokens(
            access=str(refresh.access_token), refresh=str(refresh)
        )

    @staticmethod
    def change_password(
        user: User,
        current_password: str,
        new_password: str,
    ) -> User:
        """Replace the user password after checking the current one.

        Args:
            user: Authenticated user.
            current_password: Password currently in use.
            new_password: Password that replaces the current one.

        Returns:
            The updated user.

        Raises:
            InvalidCredentialsError: If the current password is wrong.
        """
        if not user.check_password(current_password):
            raise InvalidCredentialsError
        return UserRepository.update_password(user, raw_password=new_password)

    @staticmethod
    def change_name(user: User, first_name: str, last_name: str) -> User:
        """Change the first and last names of the user.

        Args:
            user: Authenticated user.
            first_name: New first name.
            last_name: New last name.

        Returns:
            The updated user.
        """
        return UserRepository.update_name(
            user, first_name=first_name, last_name=last_name
        )
