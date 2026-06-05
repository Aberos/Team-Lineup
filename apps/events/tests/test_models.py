"""Tests for events models."""

from django.test import TestCase

from apps.events import models


class TestEventModelDocstrings(TestCase):
    """Test required docstrings in events models."""

    def test_models_possuem_docstrings_obrigatorias(self) -> None:
        """Validate required docstrings in events models.

        Returns:
            None: This test does not return a value.
        """
        self.assertIsNotNone(models.__doc__)
        self.assertIsNotNone(models.Event.__doc__)
        self.assertIsNotNone(models.EventParticipation.__doc__)
        self.assertIsNotNone(models.EventTeam.__doc__)
        self.assertIsNotNone(models.TeamMembership.__doc__)
        self.assertIsNotNone(models.EventMatch.__doc__)
