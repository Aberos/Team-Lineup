"""Models for player registration and roles."""

from django.db import models

PLAYER_NAME_MAX_LENGTH = 100
PLAYER_PHONE_MAX_LENGTH = 20
PLAYER_EMAIL_MAX_LENGTH = 100
ROLE_NAME_MAX_LENGTH = 100


class Player(models.Model):
    """Represent a registered player."""

    name = models.CharField(max_length=PLAYER_NAME_MAX_LENGTH)
    birthday = models.DateField()
    phone = models.CharField(max_length=PLAYER_PHONE_MAX_LENGTH)
    email = models.EmailField(max_length=PLAYER_EMAIL_MAX_LENGTH, unique=True)
    number = models.IntegerField()

    def __str__(self) -> str:
        return str(self.name)


class Role(models.Model):
    """Represent a player role."""

    name = models.CharField(max_length=ROLE_NAME_MAX_LENGTH)

    def __str__(self) -> str:
        return str(self.name)


class PlayerRole(models.Model):
    """Represent the relationship between a player and a role."""

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["player", "role"], name="unique_player_role"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.player.name} - {self.role.name}"
