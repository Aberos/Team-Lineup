"""Tests for the players services."""

import shutil
import tempfile
from datetime import date
from io import BytesIO, StringIO
from typing import Any

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from PIL import Image

from apps.players.exceptions import (
    ActiveFormulaDeletionError,
    AttributeAbbreviationAlreadyExistsError,
    AttributeNameAlreadyExistsError,
    CardSlotTakenError,
    FormulaActivationError,
    FormulaError,
    PlayerAttributeAlreadyExistsError,
    PlayerEmailAlreadyExistsError,
    PlayerRoleAlreadyAssignedError,
)
from apps.players.formula_engine import FormulaInput, compile_formula
from apps.players.models import (
    Attribute,
    Player,
    PlayerAttribute,
    PlayerOrdering,
    PlayerRole,
    Role,
)
from apps.players.services import (
    DEFAULT_ATTRIBUTE_NAMES,
    DEFAULT_ROLE_NAMES,
    AttributeService,
    FormulaService,
    OverallService,
    PlayerService,
)

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
        self.other = Role.objects.create(name="Striker")

    def _primary_names(self) -> list[str]:
        """Return the names of the primary roles of the fixture player."""
        return [
            item.role.name
            for item in PlayerService.list_player_roles(self.player.id)
            if item.is_primary
        ]

    def test_first_role_becomes_primary(self) -> None:
        """Mark the first assigned role as primary, not the second."""
        first = PlayerService.assign_role(self.player.id, self.role.id)
        second = PlayerService.assign_role(self.player.id, self.other.id)

        self.assertTrue(first.is_primary)
        self.assertFalse(second.is_primary)
        self.assertEqual(
            [
                item.role.name
                for item in PlayerService.list_player_roles(self.player.id)
            ],
            ["Goalkeeper", "Striker"],
        )

    def test_set_primary_role_moves_the_flag(self) -> None:
        """Keep a single primary role after switching it."""
        PlayerService.assign_role(self.player.id, self.role.id)
        PlayerService.assign_role(self.player.id, self.other.id)

        PlayerService.set_primary_role(self.player.id, self.other.id)

        self.assertEqual(self._primary_names(), ["Striker"])

    def test_set_primary_on_unassigned_role_raises(self) -> None:
        """Raise PlayerRole.DoesNotExist for a role the player lacks."""
        with self.assertRaises(PlayerRole.DoesNotExist):
            PlayerService.set_primary_role(self.player.id, self.role.id)

    def test_removing_primary_promotes_oldest_role(self) -> None:
        """Promote the oldest remaining role when the primary leaves."""
        PlayerService.assign_role(self.player.id, self.role.id)
        PlayerService.assign_role(self.player.id, self.other.id)

        PlayerService.remove_role(self.player.id, self.role.id)

        self.assertEqual(self._primary_names(), ["Striker"])

    def test_deleting_primary_role_promotes_oldest_role(self) -> None:
        """Promote another role when the primary role is deleted."""
        PlayerService.assign_role(self.player.id, self.role.id)
        PlayerService.assign_role(self.player.id, self.other.id)

        PlayerService.delete_role(self.role.id)

        self.assertEqual(self._primary_names(), ["Striker"])

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

    def test_remove_unassigned_role_raises(self) -> None:
        """Raise PlayerRole.DoesNotExist when the role is not assigned."""
        with self.assertRaises(PlayerRole.DoesNotExist):
            PlayerService.remove_role(self.player.id, self.role.id)


def _create_attribute(
    name: str = "Passe", abbreviation: str = "PAS", card_order: int | None = 1
) -> Attribute:
    """Create an attribute through the service."""
    return AttributeService.create_attribute(
        name=name, abbreviation=abbreviation, card_order=card_order
    )


class AttributeServiceTests(TestCase):
    """Tests for AttributeService."""

    def setUp(self) -> None:
        self.player = PlayerService.create_player(**_player_fields())

    def test_create_attribute_normalizes_fields(self) -> None:
        """Strip the name and uppercase the abbreviation."""
        attribute = _create_attribute(name="  Passe ", abbreviation=" pas ")

        self.assertEqual(
            (attribute.name, attribute.abbreviation), ("Passe", "PAS")
        )

    def test_create_attribute_conflicts_raise(self) -> None:
        """Raise for a repeated name, abbreviation or card slot."""
        _create_attribute()

        with self.assertRaises(AttributeNameAlreadyExistsError):
            _create_attribute(name="PASSE", abbreviation="PSS", card_order=2)
        with self.assertRaises(AttributeAbbreviationAlreadyExistsError):
            _create_attribute(
                name="Lançamento", abbreviation="pas", card_order=2
            )
        with self.assertRaises(CardSlotTakenError):
            _create_attribute(
                name="Lançamento", abbreviation="LAN", card_order=1
            )

    def test_update_attribute_keeps_own_values(self) -> None:
        """Allow saving an attribute with its current values."""
        attribute = _create_attribute()

        updated = AttributeService.update_attribute(
            attribute.id, name="Passe", abbreviation="PAS", card_order=1
        )

        self.assertEqual(updated.card_order, 1)

    def test_update_to_values_of_other_raises(self) -> None:
        """Raise when another attribute already uses the values."""
        _create_attribute()
        other = _create_attribute(
            name="Chute", abbreviation="CHU", card_order=2
        )

        with self.assertRaises(AttributeNameAlreadyExistsError):
            AttributeService.update_attribute(
                other.id, name="passe", abbreviation="CHU", card_order=2
            )
        with self.assertRaises(CardSlotTakenError):
            AttributeService.update_attribute(
                other.id, name="Chute", abbreviation="CHU", card_order=1
            )

    def test_rate_and_update_player_refresh_overall(self) -> None:
        """Store the average of card ratings as the overall."""
        passe = _create_attribute()
        chute = _create_attribute(
            name="Chute", abbreviation="CHU", card_order=2
        )
        hidden = _create_attribute(
            name="Liderança", abbreviation="LID", card_order=None
        )

        AttributeService.rate_player(
            self.player.id, attribute_id=passe.id, value=60
        )
        AttributeService.rate_player(
            self.player.id, attribute_id=chute.id, value=75
        )
        AttributeService.rate_player(
            self.player.id, attribute_id=hidden.id, value=10
        )
        self.player.refresh_from_db()
        self.assertEqual(self.player.overall, 68)

        AttributeService.update_rating(
            self.player.id, attribute_id=passe.id, value=85
        )
        self.player.refresh_from_db()
        self.assertEqual(self.player.overall, 80)

        AttributeService.remove_rating(self.player.id, passe.id)
        AttributeService.remove_rating(self.player.id, chute.id)
        self.player.refresh_from_db()
        self.assertIsNone(self.player.overall)

    def test_card_changes_refresh_every_overall(self) -> None:
        """Recalculate overalls when an attribute leaves or joins cards."""
        passe = _create_attribute()
        chute = _create_attribute(
            name="Chute", abbreviation="CHU", card_order=2
        )
        AttributeService.rate_player(
            self.player.id, attribute_id=passe.id, value=60
        )
        AttributeService.rate_player(
            self.player.id, attribute_id=chute.id, value=80
        )

        AttributeService.update_attribute(
            chute.id, name="Chute", abbreviation="CHU", card_order=None
        )
        self.player.refresh_from_db()
        self.assertEqual(self.player.overall, 60)

        AttributeService.delete_attribute(passe.id)
        self.player.refresh_from_db()
        self.assertIsNone(self.player.overall)

    def test_rate_twice_raises(self) -> None:
        """Raise when the player already has a rating for the attribute."""
        attribute = _create_attribute()
        AttributeService.rate_player(
            self.player.id, attribute_id=attribute.id, value=60
        )

        with self.assertRaises(PlayerAttributeAlreadyExistsError):
            AttributeService.rate_player(
                self.player.id, attribute_id=attribute.id, value=70
            )

    def test_rate_missing_attribute_raises(self) -> None:
        """Raise Attribute.DoesNotExist for an unknown attribute."""
        with self.assertRaises(Attribute.DoesNotExist):
            AttributeService.rate_player(
                self.player.id, attribute_id=_MISSING_ID, value=10
            )

    def test_list_ratings_of_missing_player_raises(self) -> None:
        """Raise Player.DoesNotExist for an unknown player."""
        with self.assertRaises(Player.DoesNotExist):
            AttributeService.list_player_attributes(_MISSING_ID)

    def test_remove_missing_rating_raises(self) -> None:
        """Raise PlayerAttribute.DoesNotExist when there is no rating."""
        attribute = _create_attribute()

        with self.assertRaises(PlayerAttribute.DoesNotExist):
            AttributeService.remove_rating(self.player.id, attribute.id)


class OverallServiceTests(TestCase):
    """Tests for OverallService."""

    def test_calculate_rounds_half_up(self) -> None:
        """Round the average to the nearest integer, halves up."""
        self.assertEqual(OverallService.calculate([60, 75]), 68)
        self.assertEqual(OverallService.calculate([70]), 70)
        self.assertIsNone(OverallService.calculate([]))


class PlayerCardListingTests(TestCase):
    """Tests for PlayerService.list_player_cards."""

    def test_builds_cards_with_every_card_attribute(self) -> None:
        """Fill unrated card attributes with None, in slot order."""
        player = PlayerService.create_player(**_player_fields())
        role = Role.objects.create(name="MID")
        PlayerService.assign_role(player.id, role.id)
        speed = _create_attribute(
            name="Velocidade", abbreviation="VEL", card_order=1
        )
        _create_attribute(name="Passe", abbreviation="PAS", card_order=2)
        AttributeService.rate_player(
            player.id, attribute_id=speed.id, value=90
        )

        page = PlayerService.list_player_cards(
            search="",
            role_id=None,
            ordering=PlayerOrdering.NAME,
            page=1,
            page_size=24,
        )

        self.assertEqual(page.count, 1)
        card = page.items[0]
        self.assertEqual(card.player.overall, 90)
        self.assertEqual([item.role.name for item in card.roles], ["MID"])
        self.assertEqual(
            [(item.abbreviation, item.value) for item in card.card_attributes],
            [("VEL", 90), ("PAS", None)],
        )

    def test_second_page_skips_first_items(self) -> None:
        """Skip the players of previous pages."""
        for index in range(3):
            PlayerService.create_player(
                **_player_fields(
                    name=f"Jogador {index}", email=f"j{index}@example.com"
                )
            )

        page = PlayerService.list_player_cards(
            search="",
            role_id=None,
            ordering=PlayerOrdering.NAME,
            page=2,
            page_size=2,
        )

        self.assertEqual(page.count, 3)
        self.assertEqual(
            [card.player.name for card in page.items], ["Jogador 2"]
        )


class PlayerPhotoServiceTests(TestCase):
    """Tests for the photo rules of PlayerService."""

    def setUp(self) -> None:
        media_root = tempfile.mkdtemp()
        override = override_settings(MEDIA_ROOT=media_root)
        override.enable()
        self.addCleanup(override.disable)
        self.addCleanup(shutil.rmtree, media_root, True)
        self.player = PlayerService.create_player(**_player_fields())

    def test_update_and_remove_photo(self) -> None:
        """Store a photo and remove it later."""
        buffer = BytesIO()
        Image.new("RGB", (4, 4), "white").save(buffer, format="PNG")
        upload = SimpleUploadedFile("a.png", buffer.getvalue(), "image/png")

        updated = PlayerService.update_photo(self.player.id, upload)
        self.assertTrue(updated.photo.name.startswith("players/"))

        removed = PlayerService.remove_photo(self.player.id)
        self.assertFalse(removed.photo)

    def test_photo_of_missing_player_raises(self) -> None:
        """Raise Player.DoesNotExist for an unknown player."""
        with self.assertRaises(Player.DoesNotExist):
            PlayerService.remove_photo(_MISSING_ID)


class SeedDefaultCatalogTests(TestCase):
    """Tests for the default catalog seed."""

    def test_seed_creates_default_roles_and_attributes(self) -> None:
        """Create every default role and attribute."""
        result = PlayerService.seed_default_catalog()

        self.assertEqual(
            sorted(role.name for role in result.roles), ["ATK", "DEF", "MID"]
        )
        self.assertEqual(
            set(Attribute.objects.values_list("name", flat=True)),
            set(DEFAULT_ATTRIBUTE_NAMES),
        )

    def test_seed_is_idempotent(self) -> None:
        """Create nothing when the seed runs again."""
        PlayerService.seed_default_catalog()

        result = PlayerService.seed_default_catalog()

        self.assertEqual((result.roles, result.attributes), ([], []))
        self.assertEqual(Role.objects.count(), len(DEFAULT_ROLE_NAMES))

    def test_seed_keeps_existing_names_ignoring_case(self) -> None:
        """Skip names that already exist with another case."""
        Role.objects.create(name="def")
        Attribute.objects.create(name="passe", abbreviation="PSS")

        result = PlayerService.seed_default_catalog()

        self.assertNotIn("DEF", [role.name for role in result.roles])
        self.assertEqual(Role.objects.filter(name__iexact="def").count(), 1)
        self.assertEqual(
            Attribute.objects.filter(name__iexact="passe").count(), 1
        )

    def test_seed_places_defaults_on_free_card_slots(self) -> None:
        """Give default attributes their slots unless already taken."""
        Attribute.objects.create(
            name="Liderança", abbreviation="LID", card_order=1
        )

        PlayerService.seed_default_catalog()

        speed = Attribute.objects.get(name="Velocidade")
        passing = Attribute.objects.get(name="Passe")
        self.assertEqual((speed.abbreviation, speed.card_order), ("VEL", None))
        self.assertEqual(
            (passing.abbreviation, passing.card_order), ("PAS", 3)
        )

    def test_command_reports_created_records(self) -> None:
        """Print what was created and nothing on the second run."""
        first = StringIO()
        second = StringIO()

        call_command("seed_defaults", stdout=first)
        call_command("seed_defaults", stdout=second)

        self.assertIn("Funções criadas: DEF, MID, ATK", first.getvalue())
        self.assertIn("Funções criadas: nenhuma", second.getvalue())
        self.assertIn("Atributos criados: nenhum", second.getvalue())


_AVERAGE_WITH_DEFENSE_BONUS = """
function overall(notas, funcoes, principal)
  local soma, total = 0, 0
  for _, valor in pairs(notas) do
    soma = soma + valor
    total = total + 1
  end
  if total == 0 then return nil end
  local media = soma / total
  if principal == "DEF" then media = media + 10 end
  return math.min(100, media)
end
"""


class FormulaEngineSandboxTests(TestCase):
    """Tests for the Lua sandbox of the formula engine."""

    def _evaluate(self, script: str) -> int | None:
        """Compile and run a script for a fixed player."""
        return compile_formula(script).evaluate(
            FormulaInput({"VEL": 80, "PAS": 61}, ["MID", "DEF"], "DEF")
        )

    def test_valid_formula_receives_ratings_roles_and_primary(self) -> None:
        """Return the rounded value computed by the script."""
        self.assertEqual(self._evaluate(_AVERAGE_WITH_DEFENSE_BONUS), 81)
        self.assertEqual(
            self._evaluate(
                "function overall(n, f, p) return #f * 10 + n.VEL / 10 end"
            ),
            28,
        )
        self.assertIsNone(self._evaluate("function overall() return nil end"))

    def test_dangerous_globals_are_not_available(self) -> None:
        """Hide os, io, require, load, debug, pcall, python and random."""
        scripts = [
            "function overall() return os.time() end",
            "function overall() io.write('x') return 1 end",
            "function overall() require('os') return 1 end",
            "function overall() return load('return 1')() end",
            "function overall() debug.sethook() return 1 end",
            "function overall() return pcall(error) end",
            "function overall() return python.eval('1') end",
            "function overall() return math.random(1, 10) end",
            "function overall() return string.dump(overall) end",
            "function overall() return coroutine.create(overall) end",
        ]

        for script in scripts:
            with self.subTest(script=script), self.assertRaises(FormulaError):
                self._evaluate(script)

    def test_limits_stop_endless_and_greedy_scripts(self) -> None:
        """Stop infinite loops and memory exhaustion with a clear message."""
        cases = {
            "while true do end": "instruções",
            "function overall() while true do end end": "instruções",
            "function overall() return #string.rep('x', 1e9) end": "memória",
        }

        for script, message in cases.items():
            with self.subTest(script=script):
                with self.assertRaises(FormulaError) as context:
                    self._evaluate(script)
                self.assertIn(message, context.exception.message)
                self.assertNotIn("traceback", context.exception.message)

    def test_invalid_scripts_and_results_are_rejected(self) -> None:
        """Reject syntax errors, missing entry point and invalid values."""
        scripts = [
            "function overall( return",
            "x = 1",
            "function overall() return 150 end",
            "function overall() return -1 end",
            "function overall() return 'alto' end",
            "function overall() return true end",
            "function overall() return 0/0 end",
            "function overall() error('falhou') end",
        ]

        for script in scripts:
            with self.subTest(script=script), self.assertRaises(FormulaError):
                self._evaluate(script)


class FormulaServiceTests(TestCase):
    """Tests for FormulaService and the use of the active formula."""

    def setUp(self) -> None:
        self.author = get_user_model().objects.create_user(
            username="admin", password="secret-pass", is_staff=True
        )
        self.speed = _create_attribute(
            name="Velocidade", abbreviation="VEL", card_order=1
        )
        self.defense_role = Role.objects.create(name="DEF")
        self.ana = PlayerService.create_player(**_player_fields())
        self.bia = PlayerService.create_player(
            **_player_fields(name="Bia", email="bia@example.com")
        )
        AttributeService.rate_player(
            self.ana.id, attribute_id=self.speed.id, value=70
        )
        AttributeService.rate_player(
            self.bia.id, attribute_id=self.speed.id, value=50
        )
        PlayerService.assign_role(self.ana.id, self.defense_role.id)

    def _create(self, script: str = _AVERAGE_WITH_DEFENSE_BONUS) -> Any:
        """Save a formula version by the fixture author."""
        return FormulaService.create_formula(
            script=script, description=" Bônus DEF ", author=self.author
        )

    def _overalls(self) -> tuple[int | None, int | None]:
        """Return the stored overall of Ana and Bia."""
        self.ana.refresh_from_db()
        self.bia.refresh_from_db()
        return self.ana.overall, self.bia.overall

    def test_create_formula_checks_the_script(self) -> None:
        """Save valid scripts inactive and reject broken ones."""
        formula = self._create()

        self.assertFalse(formula.is_active)
        self.assertEqual(formula.description, "Bônus DEF")
        with self.assertRaises(FormulaError):
            self._create("function overall( return")

    def test_preview_does_not_store_anything(self) -> None:
        """Return current and new values without changing overalls."""
        results = FormulaService.preview(_AVERAGE_WITH_DEFENSE_BONUS, limit=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(
            (results[0].player_name, results[0].current_overall),
            ("Ana Souza", 70),
        )
        self.assertEqual(results[0].new_overall, 80)
        self.assertEqual(self._overalls(), (70, 50))

    def test_preview_reports_errors_per_player(self) -> None:
        """Keep the error of each player instead of failing everything."""
        script = (
            "function overall(n, f, p) "
            "if p == 'DEF' then error('sem defesa') end return 1 end"
        )

        results = FormulaService.preview(script, limit=10)

        errors = {item.player_name: item.error for item in results}
        self.assertIn("sem defesa", errors["Ana Souza"] or "")
        self.assertIsNone(errors["Bia"])

    def test_activate_stores_new_overalls_and_is_used_later(self) -> None:
        """Recalculate everyone and keep using the formula afterwards."""
        formula = self._create()

        FormulaService.activate_formula(formula.id)

        self.assertEqual(FormulaService.get_active_formula(), formula)
        self.assertEqual(self._overalls(), (80, 50))
        PlayerService.assign_role(self.bia.id, self.defense_role.id)
        self.assertEqual(self._overalls(), (80, 60))

    def test_activation_fails_without_changes(self) -> None:
        """Keep the current state when the formula fails for a player."""
        formula = self._create(
            "function overall(n, f, p) "
            "if p == 'DEF' then error('sem defesa') end return 1 end"
        )

        with self.assertRaises(FormulaActivationError) as context:
            FormulaService.activate_formula(formula.id)

        self.assertEqual(context.exception.failures[0][1], "Ana Souza")
        self.assertIsNone(FormulaService.get_active_formula())
        self.assertEqual(self._overalls(), (70, 50))

    def test_deactivate_goes_back_to_average(self) -> None:
        """Recalculate overalls with the average after deactivation."""
        FormulaService.activate_formula(self._create().id)

        FormulaService.deactivate_formulas()

        self.assertIsNone(FormulaService.get_active_formula())
        self.assertEqual(self._overalls(), (70, 50))

    def test_runtime_failure_falls_back_to_average(self) -> None:
        """Use the average when the active formula fails for one player."""
        formula = self._create(
            "function overall(n) "
            "if n.VEL == 99 then error('x') end return 10 end"
        )
        FormulaService.activate_formula(formula.id)

        AttributeService.update_rating(
            self.bia.id, attribute_id=self.speed.id, value=99
        )

        self.assertEqual(self._overalls(), (10, 99))

    def test_delete_formula_rules(self) -> None:
        """Delete inactive versions and refuse the active one."""
        active = self._create()
        inactive = self._create()
        FormulaService.activate_formula(active.id)

        FormulaService.delete_formula(inactive.id)

        with self.assertRaises(ActiveFormulaDeletionError):
            FormulaService.delete_formula(active.id)
        self.assertEqual(FormulaService.list_formulas(), [active])
