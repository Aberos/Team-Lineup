"""Tests for the events repository."""

from datetime import date

from django.test import TestCase

from apps.events.models import Event, MatchStatus, TeamMembership
from apps.events.repository import (
    EventMatchRepository,
    EventParticipationRepository,
    EventRepository,
    EventTeamRepository,
    TeamMembershipRepository,
)
from apps.players.models import Player


class EventRepositoryTests(TestCase):
    """Tests for the events repositories."""

    def setUp(self) -> None:
        self.event = EventRepository.create(
            name="Copa", event_date=date(2026, 5, 1), location="Arena"
        )
        self.player = Player.objects.create(
            name="Ana",
            birthday=date(1995, 4, 10),
            phone="11999990000",
            email="ana@example.com",
            number=10,
        )

    def test_list_all_orders_by_most_recent(self) -> None:
        """Return the most recent event first."""
        older = EventRepository.create(
            name="Antiga", event_date=date(2020, 1, 1), location="X"
        )

        self.assertEqual(EventRepository.list_all(), [self.event, older])

    def test_update_and_delete_event(self) -> None:
        """Persist new data and remove the event."""
        EventRepository.update(
            self.event,
            name="Liga",
            event_date=date(2026, 6, 1),
            location="Campo",
        )

        self.event.refresh_from_db()
        self.assertEqual(self.event.name, "Liga")
        EventRepository.delete(self.event)
        self.assertFalse(Event.objects.exists())

    def test_participation_crud(self) -> None:
        """Create, find, update and delete a participation."""
        participation = EventParticipationRepository.create(
            event=self.event, player=self.player, score=1
        )

        self.assertTrue(
            EventParticipationRepository.exists(self.event.id, self.player.id)
        )
        EventParticipationRepository.update_score(participation, score=4)
        found = EventParticipationRepository.get(self.event.id, self.player.id)
        self.assertEqual(found.score, 4)
        self.assertEqual(
            EventParticipationRepository.list_by_event(self.event.id),
            [participation],
        )
        EventParticipationRepository.delete(participation)
        self.assertFalse(
            EventParticipationRepository.exists(self.event.id, self.player.id)
        )

    def test_team_name_exists_respects_exclusion(self) -> None:
        """Ignore the excluded team when checking the name."""
        team = EventTeamRepository.create(self.event, team_name="A")

        self.assertTrue(EventTeamRepository.name_exists(self.event.id, "A"))
        self.assertFalse(
            EventTeamRepository.name_exists(
                self.event.id, "A", exclude_id=team.id
            )
        )

    def test_membership_queries(self) -> None:
        """Find the player in the event and remove it from its teams."""
        team = EventTeamRepository.create(self.event, team_name="A")
        TeamMembershipRepository.create(team, player=self.player)

        self.assertTrue(
            TeamMembershipRepository.player_in_event(
                self.event.id, self.player.id
            )
        )
        self.assertEqual(
            len(TeamMembershipRepository.list_by_team(team.id)), 1
        )
        TeamMembershipRepository.delete_by_event_and_player(
            self.event.id, self.player.id
        )
        self.assertFalse(TeamMembership.objects.exists())

    def test_match_crud(self) -> None:
        """Create, update and delete a match."""
        home = EventTeamRepository.create(self.event, team_name="A")
        away = EventTeamRepository.create(self.event, team_name="B")
        match = EventMatchRepository.create(
            event=self.event,
            team_home=home,
            team_away=away,
            score_team_home=0,
            score_team_away=0,
            match_status=MatchStatus.SCHEDULED,
        )

        EventMatchRepository.update(
            match,
            team_home=home,
            team_away=away,
            score_team_home=1,
            score_team_away=2,
            match_status=MatchStatus.ONGOING,
        )

        found = EventMatchRepository.get_for_event(self.event.id, match.id)
        self.assertEqual(found.score_team_away, 2)
        self.assertEqual(
            EventMatchRepository.list_by_event(self.event.id), [match]
        )
        EventMatchRepository.delete(match)
        self.assertEqual(EventMatchRepository.list_by_event(self.event.id), [])
