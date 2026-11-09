"""Tests for the core services."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from apps.core.exceptions import InvalidCredentialsError
from apps.core.service import CoreService


class CoreServiceTests(TestCase):
    """Tests for CoreService."""

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="tester", password="secret-pass"
        )

    def test_login_returns_access_and_refresh_tokens(self) -> None:
        """Issue access and refresh tokens for valid credentials."""
        tokens = CoreService.login(username="tester", password="secret-pass")

        self.assertEqual(
            AccessToken(tokens.access)["user_id"], str(self.user.id)
        )
        self.assertEqual(
            RefreshToken(tokens.refresh)["user_id"], str(self.user.id)
        )

    def test_login_invalid_credentials_raises(self) -> None:
        """Raise InvalidCredentialsError for a wrong password."""
        with self.assertRaises(InvalidCredentialsError):
            CoreService.login(username="tester", password="wrong")

    def test_change_password_updates_password(self) -> None:
        """Replace the password when the current one matches."""
        CoreService.change_password(
            user=self.user,
            current_password="secret-pass",
            new_password="new-secret",
        )

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("new-secret"))

    def test_change_password_wrong_current_raises(self) -> None:
        """Raise InvalidCredentialsError when the current one is wrong."""
        with self.assertRaises(InvalidCredentialsError):
            CoreService.change_password(
                user=self.user,
                current_password="wrong",
                new_password="new-secret",
            )

    def test_change_name_updates_names(self) -> None:
        """Persist the new first and last names."""
        CoreService.change_name(
            user=self.user, first_name="John", last_name="Doe"
        )

        self.user.refresh_from_db()
        self.assertEqual(self.user.get_full_name(), "John Doe")
