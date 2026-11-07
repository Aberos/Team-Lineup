"""Tests for the events services."""

from datetime import date

from django.test import TestCase

from apps.events.exceptions import (
    ParticipantAlreadyExistsError,
    PlayerAlreadyInTeamError,
    PlayerNotFoundError,
    PlayerNotParticipantError,
    TeamNameAlreadyExistsError,
    TeamNotInEventError,
)
from apps.events.models import (
    Event,
    EventMatch,
    EventParticipation,
    EventTeam,
    MatchStatus,
    TeamMembership,
)
from apps.events.services import (
    EventMatchService,
    EventParticipantService,
    EventService,
    EventTeamService,
    TeamMembershipService,
)
from apps.players.models import Player

_MISSING_ID = 999_999


class _EventServiceTestCase(TestCase):
    """Provide an event and a player for service tests."""

    def setUp(self) -> None:
        self.event = Event.objects.create(
            name="Copa", date=date(2026, 5, 1), location="Arena"
        )
        self.player = Player.objects.create(
            name="Ana",
            birthday=date(1995, 4, 10),
            phone="11999990000",
            email="ana@example.com",
            number=10,
        )


class EventServiceTests(_EventServiceTestCase):
    """Tests for EventService."""

    def test_create_event_strips_text(self) -> None:
        """Persist the event without surrounding spaces."""
        event = EventService.create_event(
            name=" Liga ", event_date=date(2026, 6, 1), location=" Campo "
        )

        self.assertEqual((event.name, event.location), ("Liga", "Campo"))

    def test_update_event_replaces_data(self) -> None:
        """Replace every field of the event."""
        event = EventService.update_event(
            self.event.id,
            name="Liga",
            event_date=date(2026, 6, 1),
            location="Campo",
        )

        self.assertEqual(event.date, date(2026, 6, 1))

    def test_delete_missing_event_raises(self) -> None:
        """Raise Event.DoesNotExist for an unknown event."""
        with self.assertRaises(Event.DoesNotExist):
            EventService.delete_event(_MISSING_ID)


class EventParticipantServiceTests(_EventServiceTestCase):
    """Tests for EventParticipantService."""

    def test_add_participant(self) -> None:
        """Register the player in the event."""
        participation = EventParticipantService.add_participant(
            self.event.id, player_id=self.player.id, score=2
        )

        self.assertEqual(participation.score, 2)

    def test_add_missing_player_raises(self) -> None:
        """Raise PlayerNotFoundError for an unknown player."""
        with self.assertRaises(PlayerNotFoundError):
            EventParticipantService.add_participant(
                self.event.id, player_id=_MISSING_ID, score=0
            )

    def test_add_participant_twice_raises(self) -> None:
        """Raise when the player already participates."""
        EventParticipantService.add_participant(
            self.event.id, player_id=self.player.id, score=0
        )

        with self.assertRaises(ParticipantAlreadyExistsError):
            EventParticipantService.add_participant(
                self.event.id, player_id=self.player.id, score=0
            )

    def test_update_score(self) -> None:
        """Change the score of a participant."""
        EventParticipation.objects.create(
            event=self.event, player=self.player, score=0
        )

        participation = EventParticipantService.update_score(
            self.event.id, player_id=self.player.id, score=7
        )

        self.assertEqual(participation.score, 7)

    def test_remove_participant_removes_memberships(self) -> None:
        """Remove the participant from the event teams too."""
        EventParticipation.objects.create(
            event=self.event, player=self.player, score=0
        )
        team = EventTeam.objects.create(event=self.event, team_name="A")
        TeamMembership.objects.create(team=team, participant=self.player)

        EventParticipantService.remove_participant(
            self.event.id, self.player.id
        )

        self.assertFalse(TeamMembership.objects.exists())
        self.assertFalse(EventParticipation.objects.exists())

    def test_list_participants_of_missing_event_raises(self) -> None:
        """Raise Event.DoesNotExist for an unknown event."""
        with self.assertRaises(Event.DoesNotExist):
            EventParticipantService.list_participants(_MISSING_ID)


class EventTeamServiceTests(_EventServiceTestCase):
    """Tests for EventTeamService."""

    def test_create_team_duplicated_name_raises(self) -> None:
        """Raise when the event already has a team with the name."""
        EventTeamService.create_team(self.event.id, team_name="A")

        with self.assertRaises(TeamNameAlreadyExistsError):
            EventTeamService.create_team(self.event.id, team_name=" A ")

    def test_rename_team_keeps_own_name(self) -> None:
        """Allow renaming a team to its current name."""
        team = EventTeamService.create_team(self.event.id, team_name="A")

        renamed = EventTeamService.rename_team(
            self.event.id, team.id, team_name="A"
        )

        self.assertEqual(renamed.team_name, "A")

    def test_get_team_of_other_event_raises(self) -> None:
        """Raise EventTeam.DoesNotExist for a team of another event."""
        team = EventTeamService.create_team(self.event.id, team_name="A")

        with self.assertRaises(EventTeam.DoesNotExist):
            EventTeamService.get_team(_MISSING_ID, team.id)


class TeamMembershipServiceTests(_EventServiceTestCase):
    """Tests for TeamMembershipService."""

    def setUp(self) -> None:
        super().setUp()
        self.team = EventTeam.objects.create(event=self.event, team_name="A")

    def test_add_member_requires_participation(self) -> None:
        """Raise when the player does not participate in the event."""
        with self.assertRaises(PlayerNotParticipantError):
            TeamMembershipService.add_member(
                self.event.id, team_id=self.team.id, player_id=self.player.id
            )

    def test_add_member_once_per_event(self) -> None:
        """Raise when the player is already in a team of the event."""
        EventParticipation.objects.create(
            event=self.event, player=self.player, score=0
        )
        TeamMembershipService.add_member(
            self.event.id, team_id=self.team.id, player_id=self.player.id
        )
        other = EventTeam.objects.create(event=self.event, team_name="B")

        with self.assertRaises(PlayerAlreadyInTeamError):
            TeamMembershipService.add_member(
                self.event.id, team_id=other.id, player_id=self.player.id
            )

    def test_add_missing_player_raises(self) -> None:
        """Raise PlayerNotFoundError for an unknown player."""
        with self.assertRaises(PlayerNotFoundError):
            TeamMembershipService.add_member(
                self.event.id, team_id=self.team.id, player_id=_MISSING_ID
            )

    def test_remove_missing_member_raises(self) -> None:
        """Raise TeamMembership.DoesNotExist for a non member."""
        with self.assertRaises(TeamMembership.DoesNotExist):
            TeamMembershipService.remove_member(
                self.event.id, team_id=self.team.id, player_id=self.player.id
            )


class EventMatchServiceTests(_EventServiceTestCase):
    """Tests for EventMatchService."""

    def setUp(self) -> None:
        super().setUp()
        self.home = EventTeam.objects.create(event=self.event, team_name="A")
        self.away = EventTeam.objects.create(event=self.event, team_name="B")

    def test_create_and_update_match(self) -> None:
        """Create a match and replace its result."""
        match = EventMatchService.create_match(
            self.event.id,
            team_home_id=self.home.id,
            team_away_id=self.away.id,
            score_team_home=0,
            score_team_away=0,
            match_status=MatchStatus.SCHEDULED,
        )

        updated = EventMatchService.update_match(
            self.event.id,
            match.id,
            team_home_id=self.home.id,
            team_away_id=self.away.id,
            score_team_home=3,
            score_team_away=1,
            match_status=MatchStatus.COMPLETED,
        )

        self.assertEqual(updated.score_team_home, 3)
        self.assertEqual(updated.status, MatchStatus.COMPLETED)

    def test_create_match_with_foreign_team_raises(self) -> None:
        """Raise TeamNotInEventError for a team of another event."""
        other_event = Event.objects.create(
            name="Outro", date=date(2026, 1, 1), location="Y"
        )
        foreign = EventTeam.objects.create(event=other_event, team_name="C")

        with self.assertRaises(TeamNotInEventError):
            EventMatchService.create_match(
                self.event.id,
                team_home_id=self.home.id,
                team_away_id=foreign.id,
                score_team_home=0,
                score_team_away=0,
                match_status=MatchStatus.SCHEDULED,
            )

    def test_delete_missing_match_raises(self) -> None:
        """Raise EventMatch.DoesNotExist for an unknown match."""
        with self.assertRaises(EventMatch.DoesNotExist):
            EventMatchService.delete_match(self.event.id, _MISSING_ID)
