"""Models for player registration and roles."""

from django.db import models


class Player(models.Model):
    """Represent a registered player."""

    name = models.CharField(max_length=100)
    birthday = models.DateField()
    telphone = models.CharField(max_length=20)
    email = models.EmailField(max_length=100, unique=True)
    number = models.IntegerField()

    def __str__(self) -> str:
        return str(self.name)


class Role(models.Model):
    """Represent a player role."""

    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return str(self.name)


class PlayerRole(models.Model):
    """Represent the relationship between a player and a role."""

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.player.name} - {self.role.name}"
