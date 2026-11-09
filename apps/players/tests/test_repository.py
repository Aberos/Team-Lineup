"""Tests for the players repository."""

import os
import shutil
import tempfile
from datetime import date
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from apps.players.models import (
    Attribute,
    OverallFormula,
    Player,
    PlayerAttribute,
    PlayerOrdering,
    PlayerRole,
    Role,
)
from apps.players.repository import (
    AttributeRepository,
    OverallFormulaRepository,
    PlayerAttributeRepository,
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


def _image_upload(name: str) -> SimpleUploadedFile:
    """Return a small PNG upload."""
    buffer = BytesIO()
    Image.new("RGB", (4, 4), "white").save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), "image/png")


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

    def test_delete_removes_player(self) -> None:
        """Remove the player."""
        player = _create_player()

        PlayerRepository.delete(player)

        self.assertFalse(Player.objects.exists())

    def test_update_overall_and_list_ids(self) -> None:
        """Store the overall and list every player id."""
        player = _create_player()

        PlayerRepository.update_overall(player.id, 77)

        player.refresh_from_db()
        self.assertEqual(player.overall, 77)
        self.assertEqual(PlayerRepository.list_ids(), [player.id])


class PlayerSearchPageTests(TestCase):
    """Tests for PlayerRepository.search_page."""

    def setUp(self) -> None:
        self.ana = _create_player()
        self.bia = PlayerRepository.create(
            name="Bia",
            birthday=date(1995, 4, 10),
            phone="1",
            email="bia@example.com",
            number=7,
        )
        self.carla = PlayerRepository.create(
            name="Carla",
            birthday=date(1995, 4, 10),
            phone="1",
            email="carla@example.com",
            number=9,
        )
        PlayerRepository.update_overall(self.ana.id, 60)
        PlayerRepository.update_overall(self.bia.id, 90)

    def _names(
        self,
        *,
        search: str = "",
        role_id: int | None = None,
        ordering: str = PlayerOrdering.NAME,
    ) -> list[str]:
        """Return the names of the first page with the given filters."""
        players, _ = PlayerRepository.search_page(
            search=search,
            role_id=role_id,
            ordering=ordering,
            offset=0,
            limit=10,
        )
        return [player.name for player in players]

    def test_orders_by_name_and_overall_with_nulls_last(self) -> None:
        """Order by name or overall, leaving players without overall last."""
        self.assertEqual(self._names(), ["Ana", "Bia", "Carla"])
        self.assertEqual(
            self._names(ordering=PlayerOrdering.OVERALL_DESC),
            ["Bia", "Ana", "Carla"],
        )
        self.assertEqual(
            self._names(ordering=PlayerOrdering.OVERALL),
            ["Ana", "Bia", "Carla"],
        )

    def test_filters_by_search_and_role(self) -> None:
        """Keep only players matching the name and having the role."""
        role = Role.objects.create(name="DEF")
        PlayerRole.objects.create(player=self.bia, role=role, is_primary=True)

        self.assertEqual(self._names(search="ar"), ["Carla"])
        self.assertEqual(self._names(role_id=role.id), ["Bia"])

    def test_paginates_and_counts(self) -> None:
        """Return the requested slice and the total of matches."""
        players, total = PlayerRepository.search_page(
            search="",
            role_id=None,
            ordering=PlayerOrdering.NAME,
            offset=1,
            limit=1,
        )

        self.assertEqual([player.name for player in players], ["Bia"])
        self.assertEqual(total, 3)

    def test_preloads_roles_and_card_ratings(self) -> None:
        """Expose primary roles first and only card ratings."""
        mid = Role.objects.create(name="MID")
        atk = Role.objects.create(name="ATK")
        PlayerRole.objects.create(player=self.ana, role=atk)
        PlayerRole.objects.create(player=self.ana, role=mid, is_primary=True)
        on_card = Attribute.objects.create(
            name="Passe", abbreviation="PAS", card_order=1
        )
        off_card = Attribute.objects.create(name="Chute", abbreviation="CHU")
        PlayerAttribute.objects.create(
            player=self.ana, attribute=on_card, value=80
        )
        PlayerAttribute.objects.create(
            player=self.ana, attribute=off_card, value=40
        )

        players, _ = PlayerRepository.search_page(
            search="Ana",
            role_id=None,
            ordering=PlayerOrdering.NAME,
            offset=0,
            limit=10,
        )

        roles = PlayerRepository.preloaded_roles(players[0])
        ratings = PlayerRepository.preloaded_card_ratings(players[0])
        self.assertEqual([item.role.name for item in roles], ["MID", "ATK"])
        self.assertEqual([item.value for item in ratings], [80])


class PlayerPhotoRepositoryTests(TestCase):
    """Tests for the photo methods of PlayerRepository."""

    def setUp(self) -> None:
        self.media_root = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media_root)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.addCleanup(shutil.rmtree, self.media_root, True)
        self.player = _create_player()

    def test_replace_photo_deletes_previous_file(self) -> None:
        """Store the new photo and delete the old file."""
        PlayerRepository.replace_photo(self.player, _image_upload("a.png"))
        first_path = self.player.photo.path

        PlayerRepository.replace_photo(self.player, _image_upload("b.png"))

        self.assertFalse(os.path.exists(first_path))
        self.assertTrue(os.path.exists(self.player.photo.path))

    def test_remove_photo_clears_field_and_file(self) -> None:
        """Delete the file and leave the field empty."""
        PlayerRepository.replace_photo(self.player, _image_upload("a.png"))
        path = self.player.photo.path

        PlayerRepository.remove_photo(self.player)

        self.player.refresh_from_db()
        self.assertFalse(self.player.photo)
        self.assertFalse(os.path.exists(path))


class PlayerRoleRepositoryTests(TestCase):
    """Tests for PlayerRoleRepository."""

    def setUp(self) -> None:
        self.player = _create_player()
        self.role = Role.objects.create(name="Goalkeeper")

    def test_create_exists_and_list_by_player(self) -> None:
        """Link a role and find it through the player."""
        player_role = PlayerRoleRepository.create(
            self.player, self.role, is_primary=True
        )

        self.assertTrue(
            PlayerRoleRepository.exists(self.player.id, self.role.id)
        )
        self.assertTrue(PlayerRoleRepository.has_any(self.player.id))
        self.assertEqual(
            PlayerRoleRepository.list_by_player(self.player.id), [player_role]
        )
        self.assertEqual(
            PlayerRoleRepository.get_primary(self.player.id), player_role
        )
        self.assertEqual(
            PlayerRoleRepository.players_with_primary(self.role.id),
            [self.player.id],
        )

    def test_set_primary_and_first_assigned(self) -> None:
        """Toggle the primary flag and find the oldest assignment."""
        first = PlayerRoleRepository.create(
            self.player, self.role, is_primary=False
        )
        other = Role.objects.create(name="Striker")
        PlayerRoleRepository.create(self.player, other, is_primary=False)

        PlayerRoleRepository.set_primary(first, is_primary=True)

        self.assertEqual(
            PlayerRoleRepository.first_assigned(self.player.id), first
        )
        self.assertEqual(
            PlayerRoleRepository.get_primary(self.player.id), first
        )

    def test_get_missing_raises(self) -> None:
        """Raise DoesNotExist when the player does not have the role."""
        with self.assertRaises(PlayerRole.DoesNotExist):
            PlayerRoleRepository.get(self.player.id, self.role.id)

    def test_delete_removes_link(self) -> None:
        """Remove the relationship."""
        player_role = PlayerRoleRepository.create(
            self.player, self.role, is_primary=True
        )

        PlayerRoleRepository.delete(player_role)

        self.assertFalse(PlayerRole.objects.exists())


class AttributeRepositoryTests(TestCase):
    """Tests for AttributeRepository and PlayerAttributeRepository."""

    def setUp(self) -> None:
        self.player = _create_player()
        self.attribute = AttributeRepository.create(
            name="Passe", abbreviation="PAS", card_order=1
        )

    def test_name_exists_ignores_case_and_exclusion(self) -> None:
        """Find names without case and ignore the excluded attribute."""
        self.assertTrue(AttributeRepository.name_exists("PASSE"))
        self.assertFalse(
            AttributeRepository.name_exists(
                "passe", exclude_id=self.attribute.id
            )
        )

    def test_update_and_delete_attribute(self) -> None:
        """Replace the fields and remove an attribute."""
        AttributeRepository.update(
            self.attribute, name="Chute", abbreviation="CHU", card_order=None
        )

        self.attribute.refresh_from_db()
        self.assertEqual(
            (
                self.attribute.name,
                self.attribute.abbreviation,
                self.attribute.card_order,
            ),
            ("Chute", "CHU", None),
        )
        AttributeRepository.delete(self.attribute)
        self.assertFalse(Attribute.objects.exists())

    def test_abbreviation_and_card_slot_checks(self) -> None:
        """Find abbreviations without case and taken card slots."""
        self.assertTrue(AttributeRepository.abbreviation_exists("pas"))
        self.assertFalse(
            AttributeRepository.abbreviation_exists(
                "PAS", exclude_id=self.attribute.id
            )
        )
        self.assertTrue(AttributeRepository.card_slot_taken(1))
        self.assertFalse(
            AttributeRepository.card_slot_taken(
                1, exclude_id=self.attribute.id
            )
        )
        self.assertFalse(AttributeRepository.card_slot_taken(2))

    def test_list_card_attributes_in_slot_order(self) -> None:
        """Return only card attributes ordered by slot."""
        first = AttributeRepository.create(
            name="Velocidade", abbreviation="VEL", card_order=2
        )
        AttributeRepository.create(
            name="Chute", abbreviation="CHU", card_order=None
        )

        self.assertEqual(
            AttributeRepository.list_card_attributes(),
            [self.attribute, first],
        )

    def test_card_ratings_ignore_attributes_off_cards(self) -> None:
        """Return only the values of attributes shown on cards."""
        off_card = AttributeRepository.create(
            name="Chute", abbreviation="CHU", card_order=None
        )
        PlayerAttributeRepository.create(
            player=self.player, attribute=self.attribute, value=70
        )
        PlayerAttributeRepository.create(
            player=self.player, attribute=off_card, value=10
        )

        self.assertEqual(
            PlayerAttributeRepository.card_ratings_by_abbreviation(
                self.player.id
            ),
            {"PAS": 70},
        )

    def test_get_missing_attribute_raises(self) -> None:
        """Raise DoesNotExist for an unknown identifier."""
        with self.assertRaises(Attribute.DoesNotExist):
            AttributeRepository.get_by_id(_MISSING_ID)

    def test_player_attribute_crud(self) -> None:
        """Create, find, update and delete a rating."""
        rating = PlayerAttributeRepository.create(
            player=self.player, attribute=self.attribute, value=50
        )

        self.assertTrue(
            PlayerAttributeRepository.exists(self.player.id, self.attribute.id)
        )
        PlayerAttributeRepository.update_value(rating, value=75)
        found = PlayerAttributeRepository.get(
            self.player.id, self.attribute.id
        )
        self.assertEqual(found.value, 75)
        self.assertEqual(
            PlayerAttributeRepository.list_by_player(self.player.id), [rating]
        )
        PlayerAttributeRepository.delete(rating)
        self.assertFalse(PlayerAttribute.objects.exists())

    def test_get_missing_rating_raises(self) -> None:
        """Raise DoesNotExist when the player has no rating."""
        with self.assertRaises(PlayerAttribute.DoesNotExist):
            PlayerAttributeRepository.get(self.player.id, self.attribute.id)


class RoleNameExistsTests(TestCase):
    """Tests for RoleRepository.name_exists."""

    def test_name_exists_ignores_case(self) -> None:
        """Find a role name regardless of case."""
        RoleRepository.create(name="DEF")

        self.assertTrue(RoleRepository.name_exists("def"))
        self.assertFalse(RoleRepository.name_exists("MID"))


class OverallFormulaRepositoryTests(TestCase):
    """Tests for OverallFormulaRepository."""

    def _create(self, description: str) -> OverallFormula:
        """Persist an inactive formula without author."""
        return OverallFormulaRepository.create(
            script="function overall() return 1 end",
            description=description,
            created_by=None,
        )

    def test_activate_keeps_a_single_active_formula(self) -> None:
        """Deactivate the previous formula when another one is activated."""
        first = self._create("primeira")
        second = self._create("segunda")

        OverallFormulaRepository.activate(first)
        OverallFormulaRepository.activate(second)

        first.refresh_from_db()
        self.assertFalse(first.is_active)
        self.assertEqual(OverallFormulaRepository.get_active(), second)
        OverallFormulaRepository.deactivate_all()
        self.assertIsNone(OverallFormulaRepository.get_active())

    def test_list_newest_first_get_and_delete(self) -> None:
        """List newest first, find by id and delete."""
        first = self._create("primeira")
        second = self._create("segunda")

        self.assertEqual(OverallFormulaRepository.list_all(), [second, first])
        self.assertEqual(OverallFormulaRepository.get_by_id(first.id), first)
        OverallFormulaRepository.delete(first)
        with self.assertRaises(OverallFormula.DoesNotExist):
            OverallFormulaRepository.get_by_id(first.id)


class PlayerFormulaLookupTests(TestCase):
    """Tests for the lookups used to feed formulas."""

    def test_list_by_name_and_players_with_role(self) -> None:
        """Order players by name, limit them and find role holders."""
        bia = PlayerRepository.create(
            name="Bia",
            birthday=date(1995, 4, 10),
            phone="1",
            email="bia@example.com",
            number=7,
        )
        ana = _create_player()
        role = Role.objects.create(name="DEF")
        PlayerRole.objects.create(player=bia, role=role, is_primary=True)

        self.assertEqual(PlayerRepository.list_by_name(), [ana, bia])
        self.assertEqual(PlayerRepository.list_by_name(1), [ana])
        self.assertEqual(
            PlayerRoleRepository.players_with_role(role.id), [bia.id]
        )
