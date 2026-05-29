from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=100)
    birthday = models.DateField()
    telphone = models.CharField(max_length=20)
    email = models.EmailField(max_length=100, unique=True)
    number = models.IntegerField()

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class PlayerRole(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.player.name} - {self.role.name}"


class Event(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Participation(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    score = models.IntegerField()

    def __str__(self):
        return f"{self.player.name} - {self.event.name}"


class EventTeam(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    team_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.team_name} - {self.event.name}"


class TeamMembership(models.Model):
    team = models.ForeignKey(EventTeam, on_delete=models.CASCADE)
    participant = models.ForeignKey(Player, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.participant.name} - {self.team.team_name}"


class EventMatch(models.Model):
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

    def __str__(self):
        return f"{self.team1.team_name} vs {self.team2.team_name} - {self.event.name}"
