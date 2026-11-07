"""Repository for the core app."""

from django.contrib.auth.models import User


class UserRepository:
    """Provide data access for authenticated users."""

    @staticmethod
    def update_password(user: User, raw_password: str) -> User:
        """Hash and persist a new password for the user.

        Args:
            user: User whose password is changed.
            raw_password: New password in plain text.

        Returns:
            The updated user.
        """
        user.set_password(raw_password)
        user.save(update_fields=["password"])
        return user

    @staticmethod
    def update_name(user: User, first_name: str, last_name: str) -> User:
        """Persist new first and last names for the user.

        Args:
            user: User whose name is changed.
            first_name: New first name.
            last_name: New last name.

        Returns:
            The updated user.
        """
        user.first_name = first_name
        user.last_name = last_name
        user.save(update_fields=["first_name", "last_name"])
        return user
