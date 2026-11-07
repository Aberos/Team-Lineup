"""Tests for the players services."""

from datetime import date
from typing import Any

from django.test import TestCase

from apps.players.exceptions import (
    PlayerEmailAlreadyExistsError,
    PlayerRoleAlreadyAssignedError,
)
from apps.players.models import Player, PlayerRole, Role
from apps.players.services import PlayerService

_MISSING_ID = 999_999


class PlayerServiceRoleTests(TestCase):
    """Tests for the role rules of PlayerService."""

    def test_create_role_strips_name(self) -> None:
        """Persist the role name without surrounding spaces."""
        role = PlayerService.create_role(name="  Goalkeeper  ")

        self.assertEqual(role.name, "Goalkeeper")
        self.assertTrue(Role.objects.filter(name="Goalkeeper").exists())

    def test_list_roles_returns_models(self) -> None:
        """Return role instances ordered by name."""
        Role.objects.create(name="Striker")
        Role.objects.create(name="Goalkeeper")

        roles = PlayerService.list_roles()

        self.assertEqual(
            [role.name for role in roles], ["Goalkeeper", "Striker"]
        )

    def test_update_role_renames(self) -> None:
        """Rename an existing role."""
        role = Role.objects.create(name="Goalkeeper")

        updated = PlayerService.update_role(role.id, name=" Defender ")

        self.assertEqual(updated.name, "Defender")

    def test_update_missing_role_raises(self) -> None:
        """Raise DoesNotExist when updating an unknown role."""
        with self.assertRaises(Role.DoesNotExist):
            PlayerService.update_role(_MISSING_ID, name="Defender")

    def test_delete_role_removes_it(self) -> None:
        """Remove an existing role."""
        role = Role.objects.create(name="Goalkeeper")

        PlayerService.delete_role(role.id)

        self.assertFalse(Role.objects.filter(id=role.id).exists())

    def test_delete_missing_role_raises(self) -> None:
        """Raise DoesNotExist when deleting an unknown role."""
        with self.assertRaises(Role.DoesNotExist):
            PlayerService.delete_role(_MISSING_ID)


def _player_fields(**overrides: object) -> dict[str, Any]:
    """Return valid keyword arguments to create a player."""
    fields: dict[str, Any] = {
        "name": " Ana Souza ",
        "birthday": date(1995, 4, 10),
        "phone": "11999990000",
        "email": " Ana@Example.com ",
        "number": 10,
    }
    fields.update(overrides)
    return fields


class PlayerServicePlayerTests(TestCase):
    """Tests for the player rules of PlayerService."""

    def test_create_player_normalizes_data(self) -> None:
        """Strip the name and lowercase the email."""
        player = PlayerService.create_player(**_player_fields())

        self.assertEqual(player.name, "Ana Souza")
        self.assertEqual(player.email, "ana@example.com")

    def test_create_player_duplicated_email_raises(self) -> None:
        """Raise when the email is already in use."""
        PlayerService.create_player(**_player_fields())

        with self.assertRaises(PlayerEmailAlreadyExistsError):
            PlayerService.create_player(
                **_player_fields(email="ANA@example.com")
            )

    def test_update_player_keeps_own_email(self) -> None:
        """Allow an update that keeps the current email."""
        player = PlayerService.create_player(**_player_fields())

        updated = PlayerService.update_player(
            player.id, **_player_fields(name="Ana Lima")
        )

        self.assertEqual(updated.name, "Ana Lima")

    def test_update_player_email_of_other_raises(self) -> None:
        """Raise when the new email belongs to another player."""
        PlayerService.create_player(**_player_fields())
        other = PlayerService.create_player(
            **_player_fields(email="other@example.com")
        )

        with self.assertRaises(PlayerEmailAlreadyExistsError):
            PlayerService.update_player(other.id, **_player_fields())

    def test_update_missing_player_raises(self) -> None:
        """Raise DoesNotExist when updating an unknown player."""
        with self.assertRaises(Player.DoesNotExist):
            PlayerService.update_player(_MISSING_ID, **_player_fields())

    def test_delete_player_removes_it(self) -> None:
        """Remove an existing player."""
        player = PlayerService.create_player(**_player_fields())

        PlayerService.delete_player(player.id)

        self.assertFalse(Player.objects.filter(id=player.id).exists())


class PlayerServicePlayerRoleTests(TestCase):
    """Tests for the role assignment rules of PlayerService."""

    def setUp(self) -> None:
        self.player = PlayerService.create_player(**_player_fields())
        self.role = Role.objects.create(name="Goalkeeper")

    def test_assign_role_links_player_and_role(self) -> None:
        """Assign the role and list it for the player."""
        PlayerService.assign_role(self.player.id, self.role.id)

        roles = PlayerService.list_player_roles(self.player.id)

        self.assertEqual(roles, [self.role])

    def test_assign_role_twice_raises(self) -> None:
        """Raise when the player already has the role."""
        PlayerService.assign_role(self.player.id, self.role.id)

        with self.assertRaises(PlayerRoleAlreadyAssignedError):
            PlayerService.assign_role(self.player.id, self.role.id)

    def test_assign_missing_role_raises(self) -> None:
        """Raise Role.DoesNotExist for an unknown role."""
        with self.assertRaises(Role.DoesNotExist):
            PlayerService.assign_role(self.player.id, _MISSING_ID)

    def test_list_roles_of_missing_player_raises(self) -> None:
        """Raise Player.DoesNotExist for an unknown player."""
        with self.assertRaises(Player.DoesNotExist):
            PlayerService.list_player_roles(_MISSING_ID)

    def test_remove_role_unlinks(self) -> None:
        """Remove the role from the player."""
        PlayerRole.objects.create(player=self.player, role=self.role)

        PlayerService.remove_role(self.player.id, self.role.id)

        self.assertFalse(PlayerRole.objects.exists())

    def test_remove_unassigned_role_raises(self) -> None:
        """Raise PlayerRole.DoesNotExist when the role is not assigned."""
        with self.assertRaises(PlayerRole.DoesNotExist):
            PlayerService.remove_role(self.player.id, self.role.id)
