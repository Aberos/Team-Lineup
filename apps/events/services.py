"""Services for the events app."""

from datetime import date

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

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
    TeamMembership,
)
from apps.events.repository import (
    EventMatchRepository,
    EventParticipationRepository,
    EventRepository,
    EventTeamRepository,
    TeamMembershipRepository,
)
from apps.players.models import Player
from apps.players.services import PlayerService


def _get_player(player_id: int) -> Player:
    """Return a player through the players service.

    Args:
        player_id: Primary key of the player.

    Returns:
        The matching player.

    Raises:
        PlayerNotFoundError: If the player does not exist.
    """
    try:
        return PlayerService.get_player_by_id(player_id)
    except ObjectDoesNotExist as error:
        raise PlayerNotFoundError from error


class EventService:
    """Business rules for events."""

    @staticmethod
    def create_event(*, name: str, event_date: date, location: str) -> Event:
        """Create an event.

        Args:
            name: Name of the event.
            event_date: Day the event happens.
            location: Place of the event.

        Returns:
            The created event.
        """
        return EventRepository.create(
            name=name.strip(),
            event_date=event_date,
            location=location.strip(),
        )

    @staticmethod
    def list_events() -> list[Event]:
        """Return every event, most recent first."""
        return EventRepository.list_all()

    @staticmethod
    def get_event_by_id(event_id: int) -> Event:
        """Return the event with the given identifier.

        Args:
            event_id: Primary key of the event.

        Returns:
            The matching event.

        Raises:
            Event.DoesNotExist: If the event does not exist.
        """
        return EventRepository.get_by_id(event_id)

    @staticmethod
    def update_event(
        event_id: int, *, name: str, event_date: date, location: str
    ) -> Event:
        """Replace the data of an event.

        Args:
            event_id: Primary key of the event.
            name: Name of the event.
            event_date: Day the event happens.
            location: Place of the event.

        Returns:
            The updated event.

        Raises:
            Event.DoesNotExist: If the event does not exist.
        """
        event = EventRepository.get_by_id(event_id)
        return EventRepository.update(
            event,
            name=name.strip(),
            event_date=event_date,
            location=location.strip(),
        )

    @staticmethod
    def delete_event(event_id: int) -> None:
        """Delete an event with its participations, teams and matches.

        Args:
            event_id: Primary key of the event.

        Raises:
            Event.DoesNotExist: If the event does not exist.
        """
        event = EventRepository.get_by_id(event_id)
        EventRepository.delete(event)


class EventParticipantService:
    """Business rules for event participants."""

    @staticmethod
    def add_participant(
        event_id: int, *, player_id: int, score: int
    ) -> EventParticipation:
        """Register a player in an event.

        Args:
            event_id: Primary key of the event.
            player_id: Primary key of the player.
            score: Initial score of the player.

        Returns:
            The created participation.

        Raises:
            Event.DoesNotExist: If the event does not exist.
            PlayerNotFoundError: If the player does not exist.
            ParticipantAlreadyExistsError: If the player already
                participates in the event.
        """
        event = EventRepository.get_by_id(event_id)
        player = _get_player(player_id)
        if EventParticipationRepository.exists(event.id, player.id):
            raise ParticipantAlreadyExistsError
        return EventParticipationRepository.create(
            event=event, player=player, score=score
        )

    @staticmethod
    def list_participants(event_id: int) -> list[EventParticipation]:
        """Return the participants of an event.

        Args:
            event_id: Primary key of the event.

        Returns:
            The participations ordered by player name.

        Raises:
            Event.DoesNotExist: If the event does not exist.
        """
        event = EventRepository.get_by_id(event_id)
        return EventParticipationRepository.list_by_event(event.id)

    @staticmethod
    def get_participant(event_id: int, player_id: int) -> EventParticipation:
        """Return the participation of a player in an event.

        Args:
            event_id: Primary key of the event.
            player_id: Primary key of the player.

        Returns:
            The matching participation.

        Raises:
            EventParticipation.DoesNotExist: If the player does not
                participate in the event.
        """
        return EventParticipationRepository.get(event_id, player_id)

    @staticmethod
    def update_score(
        event_id: int, *, player_id: int, score: int
    ) -> EventParticipation:
        """Change the score of a participant.

        Args:
            event_id: Primary key of the event.
            player_id: Primary key of the player.
            score: New score.

        Returns:
            The updated participation.

        Raises:
            EventParticipation.DoesNotExist: If the player does not
                participate in the event.
        """
        participation = EventParticipationRepository.get(event_id, player_id)
        return EventParticipationRepository.update_score(
            participation, score=score
        )

    @staticmethod
    def remove_participant(event_id: int, player_id: int) -> None:
        """Remove a player from the event and from its teams.

        Args:
            event_id: Primary key of the event.
            player_id: Primary key of the player.

        Raises:
            EventParticipation.DoesNotExist: If the player does not
                participate in the event.
        """
        participation = EventParticipationRepository.get(event_id, player_id)
        with transaction.atomic():
            TeamMembershipRepository.delete_by_event_and_player(
                event_id, player_id
            )
            EventParticipationRepository.delete(participation)


class EventTeamService:
    """Business rules for event teams."""

    @staticmethod
    def create_team(event_id: int, team_name: str) -> EventTeam:
        """Create a team for an event.

        Args:
            event_id: Primary key of the event.
            team_name: Name of the team, unique within the event.

        Returns:
            The created team.

        Raises:
            Event.DoesNotExist: If the event does not exist.
            TeamNameAlreadyExistsError: If the event already has a team
                with the name.
        """
        event = EventRepository.get_by_id(event_id)
        normalized_name = team_name.strip()
        if EventTeamRepository.name_exists(event.id, normalized_name):
            raise TeamNameAlreadyExistsError
        return EventTeamRepository.create(event, team_name=normalized_name)

    @staticmethod
    def list_teams(event_id: int) -> list[EventTeam]:
        """Return the teams of an event.

        Args:
            event_id: Primary key of the event.

        Returns:
            The teams ordered by name.

        Raises:
            Event.DoesNotExist: If the event does not exist.
        """
        event = EventRepository.get_by_id(event_id)
        return EventTeamRepository.list_by_event(event.id)

    @staticmethod
    def get_team(event_id: int, team_id: int) -> EventTeam:
        """Return a team of an event.

        Args:
            event_id: Primary key of the event.
            team_id: Primary key of the team.

        Returns:
            The matching team.

        Raises:
            EventTeam.DoesNotExist: If the team does not belong to the
                event.
        """
        return EventTeamRepository.get_for_event(event_id, team_id)

    @staticmethod
    def rename_team(event_id: int, team_id: int, team_name: str) -> EventTeam:
        """Rename a team of an event.

        Args:
            event_id: Primary key of the event.
            team_id: Primary key of the team.
            team_name: New name, unique within the event.

        Returns:
            The updated team.

        Raises:
            EventTeam.DoesNotExist: If the team does not belong to the
                event.
            TeamNameAlreadyExistsError: If another team of the event uses
                the name.
        """
        team = EventTeamRepository.get_for_event(event_id, team_id)
        normalized_name = team_name.strip()
        if EventTeamRepository.name_exists(
            event_id, normalized_name, exclude_id=team.id
        ):
            raise TeamNameAlreadyExistsError
        return EventTeamRepository.update_name(team, team_name=normalized_name)

    @staticmethod
    def delete_team(event_id: int, team_id: int) -> None:
        """Delete a team with its memberships and matches.

        Args:
            event_id: Primary key of the event.
            team_id: Primary key of the team.

        Raises:
            EventTeam.DoesNotExist: If the team does not belong to the
                event.
        """
        team = EventTeamRepository.get_for_event(event_id, team_id)
        EventTeamRepository.delete(team)


class TeamMembershipService:
    """Business rules for team memberships."""

    @staticmethod
    def add_member(
        event_id: int, *, team_id: int, player_id: int
    ) -> TeamMembership:
        """Add an event participant to a team of the same event.

        Args:
            event_id: Primary key of the event.
            team_id: Primary key of the team.
            player_id: Primary key of the player.

        Returns:
            The created membership.

        Raises:
            EventTeam.DoesNotExist: If the team does not belong to the
                event.
            PlayerNotFoundError: If the player does not exist.
            PlayerNotParticipantError: If the player does not participate
                in the event.
            PlayerAlreadyInTeamError: If the player is already in a team of
                the event.
        """
        team = EventTeamRepository.get_for_event(event_id, team_id)
        player = _get_player(player_id)
        if not EventParticipationRepository.exists(event_id, player.id):
            raise PlayerNotParticipantError
        if TeamMembershipRepository.player_in_event(event_id, player.id):
            raise PlayerAlreadyInTeamError
        return TeamMembershipRepository.create(team, player=player)

    @staticmethod
    def list_members(event_id: int, team_id: int) -> list[TeamMembership]:
        """Return the members of a team.

        Args:
            event_id: Primary key of the event.
            team_id: Primary key of the team.

        Returns:
            The memberships ordered by player name.

        Raises:
            EventTeam.DoesNotExist: If the team does not belong to the
                event.
        """
        team = EventTeamRepository.get_for_event(event_id, team_id)
        return TeamMembershipRepository.list_by_team(team.id)

    @staticmethod
    def remove_member(event_id: int, *, team_id: int, player_id: int) -> None:
        """Remove a player from a team.

        Args:
            event_id: Primary key of the event.
            team_id: Primary key of the team.
            player_id: Primary key of the player.

        Raises:
            EventTeam.DoesNotExist: If the team does not belong to the
                event.
            TeamMembership.DoesNotExist: If the player is not in the team.
        """
        team = EventTeamRepository.get_for_event(event_id, team_id)
        membership = TeamMembershipRepository.get(team.id, player_id)
        TeamMembershipRepository.delete(membership)


def _get_event_team(event_id: int, team_id: int) -> EventTeam:
    """Return a team referenced in a match payload.

    Args:
        event_id: Primary key of the event.
        team_id: Primary key of the team.

    Returns:
        The matching team.

    Raises:
        TeamNotInEventError: If the team does not belong to the event.
    """
    try:
        return EventTeamRepository.get_for_event(event_id, team_id)
    except EventTeam.DoesNotExist as error:
        raise TeamNotInEventError from error


class EventMatchService:
    """Business rules for event matches."""

    @staticmethod
    def create_match(
        event_id: int,
        *,
        team_home_id: int,
        team_away_id: int,
        score_team_home: int,
        score_team_away: int,
        match_status: int,
    ) -> EventMatch:
        """Create a match between two teams of the event.

        Args:
            event_id: Primary key of the event.
            team_home_id: Primary key of the home team.
            team_away_id: Primary key of the away team.
            score_team_home: Score of the home team.
            score_team_away: Score of the away team.
            match_status: Value of ``MatchStatus``.

        Returns:
            The created match.

        Raises:
            Event.DoesNotExist: If the event does not exist.
            TeamNotInEventError: If a team does not belong to the event.
        """
        event = EventRepository.get_by_id(event_id)
        return EventMatchRepository.create(
            event=event,
            team_home=_get_event_team(event.id, team_home_id),
            team_away=_get_event_team(event.id, team_away_id),
            score_team_home=score_team_home,
            score_team_away=score_team_away,
            match_status=match_status,
        )

    @staticmethod
    def list_matches(event_id: int) -> list[EventMatch]:
        """Return the matches of an event.

        Args:
            event_id: Primary key of the event.

        Returns:
            The matches in creation order.

        Raises:
            Event.DoesNotExist: If the event does not exist.
        """
        event = EventRepository.get_by_id(event_id)
        return EventMatchRepository.list_by_event(event.id)

    @staticmethod
    def get_match(event_id: int, match_id: int) -> EventMatch:
        """Return a match of an event.

        Args:
            event_id: Primary key of the event.
            match_id: Primary key of the match.

        Returns:
            The matching match.

        Raises:
            EventMatch.DoesNotExist: If the match does not belong to the
                event.
        """
        return EventMatchRepository.get_for_event(event_id, match_id)

    @staticmethod
    def update_match(
        event_id: int,
        match_id: int,
        *,
        team_home_id: int,
        team_away_id: int,
        score_team_home: int,
        score_team_away: int,
        match_status: int,
    ) -> EventMatch:
        """Replace the data of a match.

        Args:
            event_id: Primary key of the event.
            match_id: Primary key of the match.
            team_home_id: Primary key of the home team.
            team_away_id: Primary key of the away team.
            score_team_home: Score of the home team.
            score_team_away: Score of the away team.
            match_status: Value of ``MatchStatus``.

        Returns:
            The updated match.

        Raises:
            EventMatch.DoesNotExist: If the match does not belong to the
                event.
            TeamNotInEventError: If a team does not belong to the event.
        """
        match = EventMatchRepository.get_for_event(event_id, match_id)
        return EventMatchRepository.update(
            match,
            team_home=_get_event_team(event_id, team_home_id),
            team_away=_get_event_team(event_id, team_away_id),
            score_team_home=score_team_home,
            score_team_away=score_team_away,
            match_status=match_status,
        )

    @staticmethod
    def delete_match(event_id: int, match_id: int) -> None:
        """Delete a match of an event.

        Args:
            event_id: Primary key of the event.
            match_id: Primary key of the match.

        Raises:
            EventMatch.DoesNotExist: If the match does not belong to the
                event.
        """
        match = EventMatchRepository.get_for_event(event_id, match_id)
        EventMatchRepository.delete(match)
