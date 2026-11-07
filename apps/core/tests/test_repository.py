"""Tests for the core repository."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.core.repository import UserRepository


class UserRepositoryTests(TestCase):
    """Tests for UserRepository."""

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="tester", password="secret-pass"
        )

    def test_update_password_hashes_and_saves(self) -> None:
        """Persist a hashed password."""
        UserRepository.update_password(self.user, raw_password="new-secret")

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("new-secret"))

    def test_update_name_saves(self) -> None:
        """Persist the new first and last names."""
        UserRepository.update_name(
            self.user, first_name="John", last_name="Doe"
        )

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "John")
        self.assertEqual(self.user.last_name, "Doe")
