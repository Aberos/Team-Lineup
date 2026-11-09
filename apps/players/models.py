"""Models for player registration, roles and attributes."""

from django.conf import settings
from django.db import models

PLAYER_NAME_MAX_LENGTH = 100
PLAYER_PHONE_MAX_LENGTH = 20
PLAYER_EMAIL_MAX_LENGTH = 100
ROLE_NAME_MAX_LENGTH = 100
ATTRIBUTE_NAME_MAX_LENGTH = 100
ATTRIBUTE_VALUE_MIN = 0
ATTRIBUTE_VALUE_MAX = 100
ATTRIBUTE_ABBREVIATION_MAX_LENGTH = 4
CARD_SLOT_MIN = 1
CARD_SLOT_MAX = 6
OVERALL_MIN = 0
OVERALL_MAX = 100
PLAYER_PHOTO_DIRECTORY = "players/"
FORMULA_DESCRIPTION_MAX_LENGTH = 200


class Player(models.Model):
    """Represent a registered player."""

    name = models.CharField(max_length=PLAYER_NAME_MAX_LENGTH)
    birthday = models.DateField()
    phone = models.CharField(max_length=PLAYER_PHONE_MAX_LENGTH)
    email = models.EmailField(max_length=PLAYER_EMAIL_MAX_LENGTH, unique=True)
    number = models.IntegerField()
    photo = models.ImageField(
        upload_to=PLAYER_PHOTO_DIRECTORY, blank=True, default=""
    )
    overall = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(overall__isnull=True)
                | models.Q(overall__gte=OVERALL_MIN, overall__lte=OVERALL_MAX),
                name="player_overall_range",
            ),
        ]

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
    is_primary = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["player", "role"], name="unique_player_role"
            ),
            models.UniqueConstraint(
                fields=["player"],
                condition=models.Q(is_primary=True),
                name="unique_primary_role_per_player",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.player.name} - {self.role.name}"


class Attribute(models.Model):
    """Represent a skill that can be rated for every player."""

    name = models.CharField(max_length=ATTRIBUTE_NAME_MAX_LENGTH, unique=True)
    abbreviation = models.CharField(
        max_length=ATTRIBUTE_ABBREVIATION_MAX_LENGTH
    )
    card_order = models.PositiveSmallIntegerField(
        null=True, blank=True, unique=True
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(card_order__isnull=True)
                | models.Q(
                    card_order__gte=CARD_SLOT_MIN,
                    card_order__lte=CARD_SLOT_MAX,
                ),
                name="attribute_card_order_range",
            ),
        ]

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


class PlayerOrdering(models.TextChoices):
    """Orderings accepted by the player listing."""

    NAME = "name", "Name"
    NAME_DESC = "-name", "Name, descending"
    OVERALL = "overall", "Overall"
    OVERALL_DESC = "-overall", "Overall, descending"


class OverallFormula(models.Model):
    """Represent a version of the Lua script that computes overalls."""

    script = models.TextField()
    description = models.CharField(
        max_length=FORMULA_DESCRIPTION_MAX_LENGTH, blank=True
    )
    is_active = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["is_active"],
                condition=models.Q(is_active=True),
                name="single_active_overall_formula",
            ),
        ]

    def __str__(self) -> str:
        return self.description or f"Fórmula {self.pk}"
