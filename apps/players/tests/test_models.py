"""Tests for players models."""

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
