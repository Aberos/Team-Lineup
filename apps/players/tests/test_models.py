"""Tests for players models."""

from datetime import date

from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.players import models


class TestPlayerModelDocstrings(TestCase):
    """Test required docstrings in players models."""

    def test_models_possuem_docstrings_obrigatorias(self) -> None:
        """Validate required docstrings in players models.

        Returns:
            None: This test does not return a value.
        """
        self.assertIsNotNone(models.__doc__)
        self.assertIsNotNone(models.Player.__doc__)
        self.assertIsNotNone(models.Role.__doc__)
        self.assertIsNotNone(models.PlayerRole.__doc__)
        self.assertIsNotNone(models.Attribute.__doc__)
        self.assertIsNotNone(models.PlayerAttribute.__doc__)
        self.assertIsNotNone(models.PlayerOrdering.__doc__)
        self.assertIsNotNone(models.OverallFormula.__doc__)


class TestPlayerAttributeConstraints(TestCase):
    """Test database constraints of player ratings."""

    def setUp(self) -> None:
        self.player = models.Player.objects.create(
            name="Ana",
            birthday=date(1995, 4, 10),
            phone="11999990000",
            email="ana@example.com",
            number=10,
        )
        self.attribute = models.Attribute.objects.create(name="Passe")

    def test_value_above_maximum_is_rejected(self) -> None:
        """Reject a rating above the maximum value."""
        with self.assertRaises(IntegrityError), transaction.atomic():
            models.PlayerAttribute.objects.create(
                player=self.player,
                attribute=self.attribute,
                value=models.ATTRIBUTE_VALUE_MAX + 1,
            )

    def test_duplicated_rating_is_rejected(self) -> None:
        """Reject a second rating for the same player and attribute."""
        models.PlayerAttribute.objects.create(
            player=self.player, attribute=self.attribute, value=10
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            models.PlayerAttribute.objects.create(
                player=self.player, attribute=self.attribute, value=20
            )


class TestPlayerCardConstraints(TestCase):
    """Test database constraints of the card data."""

    def setUp(self) -> None:
        self.player = models.Player.objects.create(
            name="Ana",
            birthday=date(1995, 4, 10),
            phone="11999990000",
            email="ana@example.com",
            number=10,
        )

    def test_single_primary_role_per_player(self) -> None:
        """Reject a second primary role for the same player."""
        defense = models.Role.objects.create(name="DEF")
        attack = models.Role.objects.create(name="ATK")
        models.PlayerRole.objects.create(
            player=self.player, role=defense, is_primary=True
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            models.PlayerRole.objects.create(
                player=self.player, role=attack, is_primary=True
            )

    def test_card_order_is_unique_and_in_range(self) -> None:
        """Reject a repeated card slot and slots outside 1 to 6."""
        models.Attribute.objects.create(
            name="Passe", abbreviation="PAS", card_order=1
        )
        models.Attribute.objects.create(name="Chute", abbreviation="CHU")
        models.Attribute.objects.create(name="Drible", abbreviation="DRI")

        invalid_orders = [1, models.CARD_SLOT_MAX + 1, 0]
        for index, card_order in enumerate(invalid_orders):
            with (
                self.subTest(card_order=card_order),
                self.assertRaises(IntegrityError),
                transaction.atomic(),
            ):
                models.Attribute.objects.create(
                    name=f"Extra {index}",
                    abbreviation=f"EX{index}",
                    card_order=card_order,
                )

    def test_overall_above_maximum_is_rejected(self) -> None:
        """Reject an overall above 100."""
        with self.assertRaises(IntegrityError), transaction.atomic():
            models.Player.objects.filter(id=self.player.id).update(
                overall=models.OVERALL_MAX + 1
            )


class TestOverallFormulaConstraints(TestCase):
    """Test database constraints of the overall formula."""

    def test_single_active_formula(self) -> None:
        """Reject a second active formula."""
        models.OverallFormula.objects.create(
            script="function overall() return 1 end", is_active=True
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            models.OverallFormula.objects.create(
                script="function overall() return 2 end", is_active=True
            )

    def test_str_uses_description(self) -> None:
        """Show the description, or a numbered fallback."""
        named = models.OverallFormula.objects.create(
            script="x", description="Bônus DEF"
        )
        unnamed = models.OverallFormula.objects.create(script="x")

        self.assertEqual(str(named), "Bônus DEF")
        self.assertEqual(str(unnamed), f"Fórmula {unnamed.pk}")
