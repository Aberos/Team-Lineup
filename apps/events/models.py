"""Models for events, teams, memberships, and matches."""

from django.db import models

from apps.players.models import Player


class Event(models.Model):
    """Represent an event."""

    name = models.CharField(max_length=100)
    date = models.DateField()
    location = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class EventParticipation(models.Model):
    """Represent a player participation in an event."""

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    score = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.player.name} - {self.event.name}"


class EventTeam(models.Model):
    """Represent a team created for an event."""

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    team_name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.team_name} - {self.event.name}"


class TeamMembership(models.Model):
    """Represent a player membership in an event team."""

    team = models.ForeignKey(EventTeam, on_delete=models.CASCADE)
    participant = models.ForeignKey(Player, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.participant.name} - {self.team.team_name}"


class EventMatch(models.Model):
    """Represent a match between two event teams."""

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    team1 = models.ForeignKey(
        EventTeam, related_name="team1_matches", on_delete=models.CASCADE
    )
    team2 = models.ForeignKey(
        EventTeam, related_name="team2_matches", on_delete=models.CASCADE
    )
    score_team1 = models.IntegerField()
    score_team2 = models.IntegerField()
    status = models.IntegerField(
        choices=[(0, "Scheduled"), (1, "Ongoing"), (2, "Completed")], default=0
    )

    def __str__(self) -> str:
        return (
            f"{self.team1.team_name} vs {self.team2.team_name} - "
            f"{self.event.name}"
        )
