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
