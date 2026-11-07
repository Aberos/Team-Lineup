"""Repository for the events app."""

from datetime import date

from apps.events.models import (
    Event,
    EventMatch,
    EventParticipation,
    EventTeam,
    TeamMembership,
)
from apps.players.models import Player


class EventRepository:
    """Provide data access for events."""

    @staticmethod
    def create(*, name: str, event_date: date, location: str) -> Event:
        """Persist a new event.

        Args:
            name: Name of the event.
            event_date: Day the event happens.
            location: Place of the event.

        Returns:
            The created event.
        """
        return Event.objects.create(
            name=name, date=event_date, location=location
        )

    @staticmethod
    def get_by_id(event_id: int) -> Event:
        """Return the event with the given identifier.

        Args:
            event_id: Primary key of the event.

        Returns:
            The matching event.

        Raises:
            Event.DoesNotExist: If no event has the given identifier.
        """
        return Event.objects.get(id=event_id)

    @staticmethod
    def list_all() -> list[Event]:
        """Return every event, most recent first."""
        return list(Event.objects.order_by("-date", "name"))

    @staticmethod
    def update(
        event: Event, *, name: str, event_date: date, location: str
    ) -> Event:
        """Replace every editable field of an event.

        Args:
            event: Event to update.
            name: Name of the event.
            event_date: Day the event happens.
            location: Place of the event.

        Returns:
            The updated event.
        """
        event.name = name
        event.date = event_date
        event.location = location
        event.save(update_fields=["name", "date", "location"])
        return event

    @staticmethod
    def delete(event: Event) -> None:
        """Remove an event.

        Args:
            event: Event to delete.
        """
        event.delete()


class EventParticipationRepository:
    """Provide data access for event participations."""

    @staticmethod
    def create(
        *, event: Event, player: Player, score: int
    ) -> EventParticipation:
        """Register a player in an event.

        Args:
            event: Event the player joins.
            player: Participating player.
            score: Initial score of the player.

        Returns:
            The created participation.
        """
        return EventParticipation.objects.create(
            event=event, player=player, score=score
        )

    @staticmethod
    def exists(event_id: int, player_id: int) -> bool:
        """Check whether the player participates in the event.

        Args:
            event_id: Primary key of the event.
            player_id: Primary key of the player.

        Returns:
            True when the participation exists.
        """
        return EventParticipation.objects.filter(
            event_id=event_id, player_id=player_id
        ).exists()

    @staticmethod
    def get(event_id: int, player_id: int) -> EventParticipation:
        """Return the participation of a player in an event.

        Args:
            event_id: Primary key of the event.
            player_id: Primary key of the player.

        Returns:
            The matching participation with its player loaded.

        Raises:
            EventParticipation.DoesNotExist: If the player does not
                participate in the event.
        """
        return EventParticipation.objects.select_related("player").get(
            event_id=event_id, player_id=player_id
        )

    @staticmethod
    def list_by_event(event_id: int) -> list[EventParticipation]:
        """Return the participations of an event ordered by player name.

        Args:
            event_id: Primary key of the event.

        Returns:
            The participations with their players loaded.
        """
        return list(
            EventParticipation.objects.select_related("player")
            .filter(event_id=event_id)
            .order_by("player__name")
        )

    @staticmethod
    def update_score(
        participation: EventParticipation, score: int
    ) -> EventParticipation:
        """Change the score of a participation.

        Args:
            participation: Participation to update.
            score: New score.

        Returns:
            The updated participation.
        """
        participation.score = score
        participation.save(update_fields=["score"])
        return participation

    @staticmethod
    def delete(participation: EventParticipation) -> None:
        """Remove a participation.

        Args:
            participation: Participation to delete.
        """
        participation.delete()


class EventTeamRepository:
    """Provide data access for event teams."""

    @staticmethod
    def create(event: Event, team_name: str) -> EventTeam:
        """Persist a new team for an event.

        Args:
            event: Event that owns the team.
            team_name: Name of the team.

        Returns:
            The created team.
        """
        return EventTeam.objects.create(event=event, team_name=team_name)

    @staticmethod
    def get_for_event(event_id: int, team_id: int) -> EventTeam:
        """Return a team that belongs to the given event.

        Args:
            event_id: Primary key of the event.
            team_id: Primary key of the team.

        Returns:
            The matching team.

        Raises:
            EventTeam.DoesNotExist: If the team does not belong to the
                event.
        """
        return EventTeam.objects.get(id=team_id, event_id=event_id)

    @staticmethod
    def list_by_event(event_id: int) -> list[EventTeam]:
        """Return the teams of an event ordered by name.

        Args:
            event_id: Primary key of the event.

        Returns:
            The teams of the event.
        """
        return list(
            EventTeam.objects.filter(event_id=event_id).order_by("team_name")
        )

    @staticmethod
    def name_exists(
        event_id: int, team_name: str, exclude_id: int | None = None
    ) -> bool:
        """Check whether the event already has a team with the name.

        Args:
            event_id: Primary key of the event.
            team_name: Name to look for.
            exclude_id: Primary key of a team to ignore in the search.

        Returns:
            True when another team of the event uses the name.
        """
        queryset = EventTeam.objects.filter(
            event_id=event_id, team_name=team_name
        )
        if exclude_id is not None:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.exists()

    @staticmethod
    def update_name(team: EventTeam, team_name: str) -> EventTeam:
        """Change the name of a team.

        Args:
            team: Team to update.
            team_name: New name of the team.

        Returns:
            The updated team.
        """
        team.team_name = team_name
        team.save(update_fields=["team_name"])
        return team

    @staticmethod
    def delete(team: EventTeam) -> None:
        """Remove a team.

        Args:
            team: Team to delete.
        """
        team.delete()


class TeamMembershipRepository:
    """Provide data access for team memberships."""

    @staticmethod
    def create(team: EventTeam, player: Player) -> TeamMembership:
        """Add a player to a team.

        Args:
            team: Team that receives the player.
            player: Player added to the team.

        Returns:
            The created membership.
        """
        return TeamMembership.objects.create(team=team, participant=player)

    @staticmethod
    def get(team_id: int, player_id: int) -> TeamMembership:
        """Return the membership of a player in a team.

        Args:
            team_id: Primary key of the team.
            player_id: Primary key of the player.

        Returns:
            The matching membership.

        Raises:
            TeamMembership.DoesNotExist: If the player is not in the team.
        """
        return TeamMembership.objects.get(
            team_id=team_id, participant_id=player_id
        )

    @staticmethod
    def list_by_team(team_id: int) -> list[TeamMembership]:
        """Return the memberships of a team ordered by player name.

        Args:
            team_id: Primary key of the team.

        Returns:
            The memberships with their players loaded.
        """
        return list(
            TeamMembership.objects.select_related("participant")
            .filter(team_id=team_id)
            .order_by("participant__name")
        )

    @staticmethod
    def player_in_event(event_id: int, player_id: int) -> bool:
        """Check whether the player is in any team of the event.

        Args:
            event_id: Primary key of the event.
            player_id: Primary key of the player.

        Returns:
            True when the player belongs to a team of the event.
        """
        return TeamMembership.objects.filter(
            team__event_id=event_id, participant_id=player_id
        ).exists()

    @staticmethod
    def delete(membership: TeamMembership) -> None:
        """Remove a membership.

        Args:
            membership: Membership to delete.
        """
        membership.delete()

    @staticmethod
    def delete_by_event_and_player(event_id: int, player_id: int) -> None:
        """Remove the player from every team of the event.

        Args:
            event_id: Primary key of the event.
            player_id: Primary key of the player.
        """
        TeamMembership.objects.filter(
            team__event_id=event_id, participant_id=player_id
        ).delete()


class EventMatchRepository:
    """Provide data access for event matches."""

    @staticmethod
    def create(
        *,
        event: Event,
        team_home: EventTeam,
        team_away: EventTeam,
        score_team_home: int,
        score_team_away: int,
        match_status: int,
    ) -> EventMatch:
        """Persist a new match.

        Args:
            event: Event that owns the match.
            team_home: Home team.
            team_away: Away team.
            score_team_home: Score of the home team.
            score_team_away: Score of the away team.
            match_status: Value of ``MatchStatus``.

        Returns:
            The created match.
        """
        return EventMatch.objects.create(
            event=event,
            team_home=team_home,
            team_away=team_away,
            score_team_home=score_team_home,
            score_team_away=score_team_away,
            status=match_status,
        )

    @staticmethod
    def get_for_event(event_id: int, match_id: int) -> EventMatch:
        """Return a match that belongs to the given event.

        Args:
            event_id: Primary key of the event.
            match_id: Primary key of the match.

        Returns:
            The matching match with its teams loaded.

        Raises:
            EventMatch.DoesNotExist: If the match does not belong to the
                event.
        """
        return EventMatch.objects.select_related("team_home", "team_away").get(
            id=match_id, event_id=event_id
        )

    @staticmethod
    def list_by_event(event_id: int) -> list[EventMatch]:
        """Return the matches of an event in creation order.

        Args:
            event_id: Primary key of the event.

        Returns:
            The matches with their teams loaded.
        """
        return list(
            EventMatch.objects.select_related("team_home", "team_away")
            .filter(event_id=event_id)
            .order_by("id")
        )

    @staticmethod
    def update(
        match: EventMatch,
        *,
        team_home: EventTeam,
        team_away: EventTeam,
        score_team_home: int,
        score_team_away: int,
        match_status: int,
    ) -> EventMatch:
        """Replace every editable field of a match.

        Args:
            match: Match to update.
            team_home: Home team.
            team_away: Away team.
            score_team_home: Score of the home team.
            score_team_away: Score of the away team.
            match_status: Value of ``MatchStatus``.

        Returns:
            The updated match.
        """
        match.team_home = team_home
        match.team_away = team_away
        match.score_team_home = score_team_home
        match.score_team_away = score_team_away
        match.status = match_status
        match.save(
            update_fields=[
                "team_home",
                "team_away",
                "score_team_home",
                "score_team_away",
                "status",
            ]
        )
        return match

    @staticmethod
    def delete(match: EventMatch) -> None:
        """Remove a match.

        Args:
            match: Match to delete.
        """
        match.delete()
