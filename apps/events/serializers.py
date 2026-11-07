"""Serializers for the events app."""

from typing import Any

from rest_framework import serializers

from apps.events.models import (
    EVENT_LOCATION_MAX_LENGTH,
    EVENT_NAME_MAX_LENGTH,
    TEAM_NAME_MAX_LENGTH,
    MatchStatus,
)

DEFAULT_SCORE = 0
MATCH_SCORE_MIN_VALUE = 0


class EventCreateSerializer(serializers.Serializer):
    """Validate the payload to create an event."""

    name = serializers.CharField(max_length=EVENT_NAME_MAX_LENGTH)
    date = serializers.DateField()
    location = serializers.CharField(max_length=EVENT_LOCATION_MAX_LENGTH)


class EventUpdateSerializer(EventCreateSerializer):
    """Validate the payload to replace an event."""


class EventListSerializer(serializers.Serializer):
    """Format an event inside a list response."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    date = serializers.DateField(read_only=True)
    location = serializers.CharField(read_only=True)


class EventDetailSerializer(EventListSerializer):
    """Format a single event response."""


class EventPlayerSerializer(serializers.Serializer):
    """Format the summary of a player inside event responses."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    number = serializers.IntegerField(read_only=True)


class EventParticipantCreateSerializer(serializers.Serializer):
    """Validate the payload to add a participant to an event."""

    player_id = serializers.IntegerField()
    score = serializers.IntegerField(default=DEFAULT_SCORE)


class EventParticipantUpdateSerializer(serializers.Serializer):
    """Validate the payload to change the score of a participant."""

    score = serializers.IntegerField()


class EventParticipantDetailSerializer(serializers.Serializer):
    """Format a single participant response."""

    player = EventPlayerSerializer(read_only=True)
    score = serializers.IntegerField(read_only=True)


class EventParticipantListSerializer(EventParticipantDetailSerializer):
    """Format a participant inside a list response."""


class EventTeamCreateSerializer(serializers.Serializer):
    """Validate the payload to create a team."""

    team_name = serializers.CharField(max_length=TEAM_NAME_MAX_LENGTH)


class EventTeamUpdateSerializer(EventTeamCreateSerializer):
    """Validate the payload to rename a team."""


class EventTeamListSerializer(serializers.Serializer):
    """Format a team inside a list response."""

    id = serializers.IntegerField(read_only=True)
    team_name = serializers.CharField(read_only=True)


class EventTeamDetailSerializer(EventTeamListSerializer):
    """Format a single team response."""


class TeamMemberCreateSerializer(serializers.Serializer):
    """Validate the payload to add a member to a team."""

    player_id = serializers.IntegerField()


class TeamMemberListSerializer(serializers.Serializer):
    """Format a team member inside a list response."""

    player = EventPlayerSerializer(source="participant", read_only=True)


class TeamMemberDetailSerializer(TeamMemberListSerializer):
    """Format a single team member response."""


class EventMatchUpdateSerializer(serializers.Serializer):
    """Validate the payload to replace a match."""

    team_home_id = serializers.IntegerField()
    team_away_id = serializers.IntegerField()
    score_team_home = serializers.IntegerField(min_value=MATCH_SCORE_MIN_VALUE)
    score_team_away = serializers.IntegerField(min_value=MATCH_SCORE_MIN_VALUE)
    status = serializers.ChoiceField(choices=MatchStatus.choices)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Reject matches of a team against itself.

        Args:
            attrs: Field values already validated.

        Returns:
            The validated values.

        Raises:
            serializers.ValidationError: If both teams are the same.
        """
        if attrs["team_home_id"] == attrs["team_away_id"]:
            raise serializers.ValidationError(
                {"team_away_id": ["Teams of a match must be different."]}
            )
        return attrs


class EventMatchCreateSerializer(EventMatchUpdateSerializer):
    """Validate the payload to create a match."""

    score_team_home = serializers.IntegerField(
        min_value=MATCH_SCORE_MIN_VALUE, default=DEFAULT_SCORE
    )
    score_team_away = serializers.IntegerField(
        min_value=MATCH_SCORE_MIN_VALUE, default=DEFAULT_SCORE
    )
    status = serializers.ChoiceField(
        choices=MatchStatus.choices, default=MatchStatus.SCHEDULED
    )


class EventMatchTeamSerializer(serializers.Serializer):
    """Format the summary of a team inside match responses."""

    id = serializers.IntegerField(read_only=True)
    team_name = serializers.CharField(read_only=True)


class EventMatchDetailSerializer(serializers.Serializer):
    """Format a single match response."""

    id = serializers.IntegerField(read_only=True)
    team_home = EventMatchTeamSerializer(read_only=True)
    team_away = EventMatchTeamSerializer(read_only=True)
    score_team_home = serializers.IntegerField(read_only=True)
    score_team_away = serializers.IntegerField(read_only=True)
    status = serializers.IntegerField(read_only=True)


class EventMatchListSerializer(EventMatchDetailSerializer):
    """Format a match inside a list response."""
