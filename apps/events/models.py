"""Models for events, teams, memberships, and matches."""

from typing import cast

from django.db import models

from apps.players.models import Player

EVENT_NAME_MAX_LENGTH = 100
EVENT_LOCATION_MAX_LENGTH = 100
TEAM_NAME_MAX_LENGTH = 100


class Event(models.Model):
    """Represent an event."""

    name = models.CharField(max_length=EVENT_NAME_MAX_LENGTH)
    date = models.DateField()
    location = models.CharField(max_length=EVENT_LOCATION_MAX_LENGTH)

    def __str__(self) -> str:
        return str(self.name)


class EventParticipation(models.Model):
    """Represent a player participation in an event."""

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    score = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["player", "event"], name="unique_event_participation"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.player.name} - {self.event.name}"


class EventTeam(models.Model):
    """Represent a team created for an event."""

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    team_name = models.CharField(max_length=TEAM_NAME_MAX_LENGTH)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "team_name"], name="unique_event_team_name"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.team_name} - {self.event.name}"


class TeamMembership(models.Model):
    """Represent a player membership in an event team."""

    team = models.ForeignKey(EventTeam, on_delete=models.CASCADE)
    participant = models.ForeignKey(Player, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["team", "participant"], name="unique_team_membership"
            ),
        ]

    def __str__(self) -> str:
        team_cast = cast(EventTeam, self.team)
        return f"{self.participant.name} - {team_cast.team_name}"


class MatchStatus(models.IntegerChoices):
    """Choices for the status of a match."""

    SCHEDULED = 0, "Scheduled"  # pyright: ignore[reportAssignmentType]
    ONGOING = 1, "Ongoing"  # pyright: ignore[reportAssignmentType]
    COMPLETED = 2, "Completed"  # pyright: ignore[reportAssignmentType]


class EventMatch(models.Model):
    """Represent a match between two event teams."""

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    team_home = models.ForeignKey(
        EventTeam, related_name="team1_matches", on_delete=models.CASCADE
    )
    team_away = models.ForeignKey(
        EventTeam, related_name="team2_matches", on_delete=models.CASCADE
    )
    score_team_home = models.IntegerField()
    score_team_away = models.IntegerField()
    status = models.IntegerField(
        choices=MatchStatus.choices,
        default=MatchStatus.SCHEDULED,  # pyright: ignore[ reportArgumentType]
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(team_home=models.F("team_away")),
                name="match_teams_must_differ",
            ),
        ]

    def __str__(self) -> str:
        home_cast = cast(EventTeam, self.team_home)
        away_cast = cast(EventTeam, self.team_away)
        event_teams = cast(Event, self.event)

        return (
            f"{home_cast.team_name} vs {away_cast.team_name} - "
            f"{event_teams.name}"
        )
