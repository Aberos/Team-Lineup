"""Serializers for the players app."""

from datetime import date

from rest_framework import serializers

from apps.players.models import (
    ATTRIBUTE_NAME_MAX_LENGTH,
    ATTRIBUTE_VALUE_MAX,
    ATTRIBUTE_VALUE_MIN,
    PLAYER_EMAIL_MAX_LENGTH,
    PLAYER_NAME_MAX_LENGTH,
    PLAYER_PHONE_MAX_LENGTH,
    ROLE_NAME_MAX_LENGTH,
)

PLAYER_NUMBER_MIN_VALUE = 0


class RoleCreateSerializer(serializers.Serializer):
    """Validate the payload to create a role."""

    name = serializers.CharField(max_length=ROLE_NAME_MAX_LENGTH)


class RoleUpdateSerializer(serializers.Serializer):
    """Validate the payload to update a role."""

    name = serializers.CharField(max_length=ROLE_NAME_MAX_LENGTH)


class RoleListSerializer(serializers.Serializer):
    """Format a role inside a list response."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)


class RoleDetailSerializer(serializers.Serializer):
    """Format a single role response."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)


class PlayerCreateSerializer(serializers.Serializer):
    """Validate the payload to create a player."""

    name = serializers.CharField(max_length=PLAYER_NAME_MAX_LENGTH)
    birthday = serializers.DateField()
    phone = serializers.CharField(max_length=PLAYER_PHONE_MAX_LENGTH)
    email = serializers.EmailField(max_length=PLAYER_EMAIL_MAX_LENGTH)
    number = serializers.IntegerField(min_value=PLAYER_NUMBER_MIN_VALUE)

    def validate_birthday(self, value: date) -> date:
        """Reject birth dates in the future.

        Args:
            value: Birth date sent by the client.

        Returns:
            The validated birth date.

        Raises:
            serializers.ValidationError: If the date is after today.
        """
        if value > date.today():
            raise serializers.ValidationError(
                "Birthday cannot be in the future."
            )
        return value


class PlayerUpdateSerializer(PlayerCreateSerializer):
    """Validate the payload to replace a player."""


class PlayerListSerializer(serializers.Serializer):
    """Format a player inside a list response."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    number = serializers.IntegerField(read_only=True)


class PlayerDetailSerializer(serializers.Serializer):
    """Format a single player response."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    birthday = serializers.DateField(read_only=True)
    phone = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    number = serializers.IntegerField(read_only=True)


class PlayerRoleCreateSerializer(serializers.Serializer):
    """Validate the payload to assign a role to a player."""

    role_id = serializers.IntegerField()


class AttributeCreateSerializer(serializers.Serializer):
    """Validate the payload to create an attribute."""

    name = serializers.CharField(max_length=ATTRIBUTE_NAME_MAX_LENGTH)


class AttributeUpdateSerializer(AttributeCreateSerializer):
    """Validate the payload to rename an attribute."""


class AttributeListSerializer(serializers.Serializer):
    """Format an attribute inside a list response."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)


class AttributeDetailSerializer(AttributeListSerializer):
    """Format a single attribute response."""


class PlayerAttributeUpdateSerializer(serializers.Serializer):
    """Validate the payload to change the rating of a player."""

    value = serializers.IntegerField(
        min_value=ATTRIBUTE_VALUE_MIN, max_value=ATTRIBUTE_VALUE_MAX
    )


class PlayerAttributeCreateSerializer(PlayerAttributeUpdateSerializer):
    """Validate the payload to rate a player in an attribute."""

    attribute_id = serializers.IntegerField()


class PlayerAttributeDetailSerializer(serializers.Serializer):
    """Format a single player rating response."""

    attribute = AttributeListSerializer(read_only=True)
    value = serializers.IntegerField(read_only=True)


class PlayerAttributeListSerializer(PlayerAttributeDetailSerializer):
    """Format a player rating inside a list response."""
