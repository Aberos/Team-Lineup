"""Models for player registration, roles and attributes."""

from django.db import models

PLAYER_NAME_MAX_LENGTH = 100
PLAYER_PHONE_MAX_LENGTH = 20
PLAYER_EMAIL_MAX_LENGTH = 100
ROLE_NAME_MAX_LENGTH = 100
ATTRIBUTE_NAME_MAX_LENGTH = 100
ATTRIBUTE_VALUE_MIN = 0
ATTRIBUTE_VALUE_MAX = 100


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


class Attribute(models.Model):
    """Represent a skill that can be rated for every player."""

    name = models.CharField(max_length=ATTRIBUTE_NAME_MAX_LENGTH, unique=True)

    def __str__(self) -> str:
        return str(self.name)


class PlayerAttribute(models.Model):
    """Represent the rating of a player in an attribute."""

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["player", "attribute"],
                name="unique_player_attribute",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    value__gte=ATTRIBUTE_VALUE_MIN,
                    value__lte=ATTRIBUTE_VALUE_MAX,
                ),
                name="player_attribute_value_range",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.player.name} - {self.attribute.name}: {self.value}"
