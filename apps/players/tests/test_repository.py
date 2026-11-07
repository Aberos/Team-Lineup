"""Tests for the players repository."""

from datetime import date

from django.test import TestCase

from apps.players.models import Player, PlayerRole, Role
from apps.players.repository import (
    PlayerRepository,
    PlayerRoleRepository,
    RoleRepository,
)

_MISSING_ID = 999_999


class RoleRepositoryTests(TestCase):
    """Tests for RoleRepository."""

    def test_create_persists_role(self) -> None:
        """Persist a new role."""
        role = RoleRepository.create(name="Goalkeeper")

        self.assertTrue(Role.objects.filter(id=role.id).exists())

    def test_get_by_id_returns_role(self) -> None:
        """Return the role with the given identifier."""
        role = Role.objects.create(name="Goalkeeper")

        self.assertEqual(RoleRepository.get_by_id(role.id), role)

    def test_get_by_id_missing_raises(self) -> None:
        """Raise DoesNotExist for an unknown identifier."""
        with self.assertRaises(Role.DoesNotExist):
            RoleRepository.get_by_id(_MISSING_ID)

    def test_list_all_orders_by_name(self) -> None:
        """Return roles ordered by name."""
        Role.objects.create(name="Striker")
        Role.objects.create(name="Goalkeeper")

        names = [role.name for role in RoleRepository.list_all()]

        self.assertEqual(names, ["Goalkeeper", "Striker"])

    def test_update_name_persists(self) -> None:
        """Persist the new role name."""
        role = Role.objects.create(name="Goalkeeper")

        RoleRepository.update_name(role, name="Defender")

        role.refresh_from_db()
        self.assertEqual(role.name, "Defender")

    def test_delete_removes_role(self) -> None:
        """Remove the role from the database."""
        role = Role.objects.create(name="Goalkeeper")

        RoleRepository.delete(role)

        self.assertFalse(Role.objects.filter(id=role.id).exists())


def _create_player(email: str = "ana@example.com") -> Player:
    """Persist a player with default data."""
    return PlayerRepository.create(
        name="Ana",
        birthday=date(1995, 4, 10),
        phone="11999990000",
        email=email,
        number=10,
    )


class PlayerRepositoryTests(TestCase):
    """Tests for PlayerRepository."""

    def test_create_and_get_by_id(self) -> None:
        """Persist a player and read it back."""
        player = _create_player()

        self.assertEqual(PlayerRepository.get_by_id(player.id), player)

    def test_get_by_id_missing_raises(self) -> None:
        """Raise DoesNotExist for an unknown identifier."""
        with self.assertRaises(Player.DoesNotExist):
            PlayerRepository.get_by_id(_MISSING_ID)

    def test_email_exists_respects_exclusion(self) -> None:
        """Ignore the excluded player when checking the email."""
        player = _create_player()

        self.assertTrue(PlayerRepository.email_exists("ana@example.com"))
        self.assertFalse(
            PlayerRepository.email_exists(
                "ana@example.com", exclude_id=player.id
            )
        )

    def test_update_persists_fields(self) -> None:
        """Persist every editable field."""
        player = _create_player()

        PlayerRepository.update(
            player,
            name="Bia",
            birthday=date(2000, 1, 1),
            phone="1100000000",
            email="bia@example.com",
            number=9,
        )

        player.refresh_from_db()
        self.assertEqual(
            (player.name, player.email, player.number),
            ("Bia", "bia@example.com", 9),
        )

    def test_list_all_and_delete(self) -> None:
        """List players by name and remove one."""
        player = _create_player()

        self.assertEqual(PlayerRepository.list_all(), [player])
        PlayerRepository.delete(player)
        self.assertEqual(PlayerRepository.list_all(), [])


class PlayerRoleRepositoryTests(TestCase):
    """Tests for PlayerRoleRepository."""

    def setUp(self) -> None:
        self.player = _create_player()
        self.role = Role.objects.create(name="Goalkeeper")

    def test_create_exists_and_list_by_player(self) -> None:
        """Link a role and find it through the player."""
        PlayerRoleRepository.create(self.player, self.role)

        self.assertTrue(
            PlayerRoleRepository.exists(self.player.id, self.role.id)
        )
        self.assertEqual(
            RoleRepository.list_by_player(self.player.id), [self.role]
        )

    def test_get_missing_raises(self) -> None:
        """Raise DoesNotExist when the player does not have the role."""
        with self.assertRaises(PlayerRole.DoesNotExist):
            PlayerRoleRepository.get(self.player.id, self.role.id)

    def test_delete_removes_link(self) -> None:
        """Remove the relationship."""
        player_role = PlayerRoleRepository.create(self.player, self.role)

        PlayerRoleRepository.delete(player_role)

        self.assertFalse(PlayerRole.objects.exists())
