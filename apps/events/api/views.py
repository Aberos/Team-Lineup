"""DRF API views for the events app."""

from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.events.exceptions import (
    ParticipantAlreadyExistsError,
    PlayerAlreadyInTeamError,
    PlayerNotFoundError,
    PlayerNotParticipantError,
    TeamNameAlreadyExistsError,
    TeamNotInEventError,
)
from apps.events.models import (
    Event,
    EventMatch,
    EventParticipation,
    EventTeam,
    TeamMembership,
)
from apps.events.serializers import (
    EventCreateSerializer,
    EventDetailSerializer,
    EventListSerializer,
    EventMatchCreateSerializer,
    EventMatchDetailSerializer,
    EventMatchListSerializer,
    EventMatchUpdateSerializer,
    EventParticipantCreateSerializer,
    EventParticipantDetailSerializer,
    EventParticipantListSerializer,
    EventParticipantUpdateSerializer,
    EventTeamCreateSerializer,
    EventTeamDetailSerializer,
    EventTeamListSerializer,
    EventTeamUpdateSerializer,
    EventUpdateSerializer,
    TeamMemberCreateSerializer,
    TeamMemberDetailSerializer,
    TeamMemberListSerializer,
)
from apps.events.services import (
    EventMatchService,
    EventParticipantService,
    EventService,
    EventTeamService,
    TeamMembershipService,
)

_EVENT_TAG = "events"
_PARTICIPANT_TAG = "events-participants"
_TEAM_TAG = "events-teams"
_MATCH_TAG = "events-matches"

_EVENT_NOT_FOUND = "Event not found."
_PARTICIPANT_NOT_FOUND = "Participant not found in this event."
_TEAM_NOT_FOUND = "Team not found in this event."
_MEMBER_NOT_FOUND = "Player is not a member of this team."
_MATCH_NOT_FOUND = "Match not found in this event."
_PLAYER_NOT_FOUND_ERRORS = {"player_id": ["Player not found."]}
_TEAM_NAME_IN_USE_ERRORS = {
    "team_name": ["This event already has a team with this name."]
}


def _not_found(detail: str) -> Response:
    """Build a 404 response with the given message.

    Args:
        detail: Message returned to the client.

    Returns:
        The 404 response.
    """
    return Response({"detail": detail}, status=status.HTTP_404_NOT_FOUND)


def _conflict(detail: str) -> Response:
    """Build a 409 response with the given message.

    Args:
        detail: Message returned to the client.

    Returns:
        The 409 response.
    """
    return Response({"detail": detail}, status=status.HTTP_409_CONFLICT)


def _event_fields(data: dict[str, Any]) -> dict[str, Any]:
    """Map validated event data to the service keyword arguments.

    Args:
        data: Validated data of an event serializer.

    Returns:
        Keyword arguments accepted by ``EventService``.
    """
    return {
        "name": data["name"],
        "event_date": data["date"],
        "location": data["location"],
    }


def _match_fields(data: dict[str, Any]) -> dict[str, Any]:
    """Map validated match data to the service keyword arguments.

    Args:
        data: Validated data of a match serializer.

    Returns:
        Keyword arguments accepted by ``EventMatchService``.
    """
    return {
        "team_home_id": data["team_home_id"],
        "team_away_id": data["team_away_id"],
        "score_team_home": data["score_team_home"],
        "score_team_away": data["score_team_away"],
        "match_status": data["status"],
    }


class EventListCreateView(APIView):
    """List and create events."""

    @extend_schema(
        tags=[_EVENT_TAG],
        description="List all events, most recent first.",
        responses={200: EventListSerializer(many=True), 401: None},
    )
    def get(self, request: Request) -> Response:
        """Return every event."""
        events = EventService.list_events()
        return Response(
            EventListSerializer(events, many=True).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=[_EVENT_TAG],
        description="Create a new event.",
        request=EventCreateSerializer,
        responses={201: EventDetailSerializer, 400: None, 401: None},
    )
    def post(self, request: Request) -> Response:
        """Create an event from the request body."""
        serializer = EventCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = EventService.create_event(
            **_event_fields(serializer.validated_data)
        )
        return Response(
            EventDetailSerializer(event).data, status=status.HTTP_201_CREATED
        )


class EventDetailView(APIView):
    """Retrieve, update and delete an event."""

    @extend_schema(
        tags=[_EVENT_TAG],
        description="Retrieve an event by ID.",
        responses={200: EventDetailSerializer, 401: None, 404: None},
    )
    def get(self, request: Request, event_id: int) -> Response:
        """Return the requested event."""
        try:
            event = EventService.get_event_by_id(event_id)
        except Event.DoesNotExist:
            return _not_found(_EVENT_NOT_FOUND)
        return Response(
            EventDetailSerializer(event).data, status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=[_EVENT_TAG],
        description="Replace the data of an event by ID.",
        request=EventUpdateSerializer,
        responses={
            200: EventDetailSerializer,
            400: None,
            401: None,
            404: None,
        },
    )
    def put(self, request: Request, event_id: int) -> Response:
        """Replace the data of the requested event."""
        serializer = EventUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            event = EventService.update_event(
                event_id, **_event_fields(serializer.validated_data)
            )
        except Event.DoesNotExist:
            return _not_found(_EVENT_NOT_FOUND)
        return Response(
            EventDetailSerializer(event).data, status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=[_EVENT_TAG],
        description=(
            "Delete an event with its participants, teams and matches."
        ),
        responses={204: None, 401: None, 404: None},
    )
    def delete(self, request: Request, event_id: int) -> Response:
        """Delete the requested event."""
        try:
            EventService.delete_event(event_id)
        except Event.DoesNotExist:
            return _not_found(_EVENT_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class EventParticipantListCreateView(APIView):
    """List and add the participants of an event."""

    @extend_schema(
        tags=[_PARTICIPANT_TAG],
        description="List the participants of an event.",
        responses={
            200: EventParticipantListSerializer(many=True),
            401: None,
            404: None,
        },
    )
    def get(self, request: Request, event_id: int) -> Response:
        """Return the participants of the requested event."""
        try:
            participants = EventParticipantService.list_participants(event_id)
        except Event.DoesNotExist:
            return _not_found(_EVENT_NOT_FOUND)
        return Response(
            EventParticipantListSerializer(participants, many=True).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=[_PARTICIPANT_TAG],
        description="Add a player to an event.",
        request=EventParticipantCreateSerializer,
        responses={
            201: EventParticipantDetailSerializer,
            400: None,
            401: None,
            404: None,
            409: None,
        },
    )
    def post(self, request: Request, event_id: int) -> Response:
        """Register the player sent in the body in the event."""
        serializer = EventParticipantCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            participation = EventParticipantService.add_participant(
                event_id, **serializer.validated_data
            )
        except Event.DoesNotExist:
            return _not_found(_EVENT_NOT_FOUND)
        except PlayerNotFoundError:
            return Response(
                _PLAYER_NOT_FOUND_ERRORS, status=status.HTTP_400_BAD_REQUEST
            )
        except ParticipantAlreadyExistsError:
            return _conflict("Player already participates in this event.")
        return Response(
            EventParticipantDetailSerializer(participation).data,
            status=status.HTTP_201_CREATED,
        )


class EventParticipantDetailView(APIView):
    """Retrieve, update and remove a participant of an event."""

    @extend_schema(
        tags=[_PARTICIPANT_TAG],
        description="Retrieve the participation of a player in an event.",
        responses={
            200: EventParticipantDetailSerializer,
            401: None,
            404: None,
        },
    )
    def get(self, request: Request, event_id: int, player_id: int) -> Response:
        """Return the requested participation."""
        try:
            participation = EventParticipantService.get_participant(
                event_id, player_id
            )
        except EventParticipation.DoesNotExist:
            return _not_found(_PARTICIPANT_NOT_FOUND)
        return Response(
            EventParticipantDetailSerializer(participation).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=[_PARTICIPANT_TAG],
        description="Change the score of a participant.",
        request=EventParticipantUpdateSerializer,
        responses={
            200: EventParticipantDetailSerializer,
            400: None,
            401: None,
            404: None,
        },
    )
    def put(self, request: Request, event_id: int, player_id: int) -> Response:
        """Replace the score of the requested participant."""
        serializer = EventParticipantUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            participation = EventParticipantService.update_score(
                event_id,
                player_id=player_id,
                score=serializer.validated_data["score"],
            )
        except EventParticipation.DoesNotExist:
            return _not_found(_PARTICIPANT_NOT_FOUND)
        return Response(
            EventParticipantDetailSerializer(participation).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=[_PARTICIPANT_TAG],
        description="Remove a player from the event and from its teams.",
        responses={204: None, 401: None, 404: None},
    )
    def delete(
        self, request: Request, event_id: int, player_id: int
    ) -> Response:
        """Remove the requested participant."""
        try:
            EventParticipantService.remove_participant(event_id, player_id)
        except EventParticipation.DoesNotExist:
            return _not_found(_PARTICIPANT_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class EventTeamListCreateView(APIView):
    """List and create the teams of an event."""

    @extend_schema(
        tags=[_TEAM_TAG],
        description="List the teams of an event.",
        responses={
            200: EventTeamListSerializer(many=True),
            401: None,
            404: None,
        },
    )
    def get(self, request: Request, event_id: int) -> Response:
        """Return the teams of the requested event."""
        try:
            teams = EventTeamService.list_teams(event_id)
        except Event.DoesNotExist:
            return _not_found(_EVENT_NOT_FOUND)
        return Response(
            EventTeamListSerializer(teams, many=True).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=[_TEAM_TAG],
        description="Create a team in an event.",
        request=EventTeamCreateSerializer,
        responses={
            201: EventTeamDetailSerializer,
            400: None,
            401: None,
            404: None,
            409: None,
        },
    )
    def post(self, request: Request, event_id: int) -> Response:
        """Create a team from the request body."""
        serializer = EventTeamCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            team = EventTeamService.create_team(
                event_id, team_name=serializer.validated_data["team_name"]
            )
        except Event.DoesNotExist:
            return _not_found(_EVENT_NOT_FOUND)
        except TeamNameAlreadyExistsError:
            return Response(
                _TEAM_NAME_IN_USE_ERRORS, status=status.HTTP_409_CONFLICT
            )
        return Response(
            EventTeamDetailSerializer(team).data,
            status=status.HTTP_201_CREATED,
        )


class EventTeamDetailView(APIView):
    """Retrieve, rename and delete a team of an event."""

    @extend_schema(
        tags=[_TEAM_TAG],
        description="Retrieve a team of an event.",
        responses={200: EventTeamDetailSerializer, 401: None, 404: None},
    )
    def get(self, request: Request, event_id: int, team_id: int) -> Response:
        """Return the requested team."""
        try:
            team = EventTeamService.get_team(event_id, team_id)
        except EventTeam.DoesNotExist:
            return _not_found(_TEAM_NOT_FOUND)
        return Response(
            EventTeamDetailSerializer(team).data, status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=[_TEAM_TAG],
        description="Rename a team of an event.",
        request=EventTeamUpdateSerializer,
        responses={
            200: EventTeamDetailSerializer,
            400: None,
            401: None,
            404: None,
            409: None,
        },
    )
    def put(self, request: Request, event_id: int, team_id: int) -> Response:
        """Rename the requested team."""
        serializer = EventTeamUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            team = EventTeamService.rename_team(
                event_id,
                team_id,
                team_name=serializer.validated_data["team_name"],
            )
        except EventTeam.DoesNotExist:
            return _not_found(_TEAM_NOT_FOUND)
        except TeamNameAlreadyExistsError:
            return Response(
                _TEAM_NAME_IN_USE_ERRORS, status=status.HTTP_409_CONFLICT
            )
        return Response(
            EventTeamDetailSerializer(team).data, status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=[_TEAM_TAG],
        description="Delete a team with its members and matches.",
        responses={204: None, 401: None, 404: None},
    )
    def delete(
        self, request: Request, event_id: int, team_id: int
    ) -> Response:
        """Delete the requested team."""
        try:
            EventTeamService.delete_team(event_id, team_id)
        except EventTeam.DoesNotExist:
            return _not_found(_TEAM_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeamMemberListCreateView(APIView):
    """List and add the members of a team."""

    @extend_schema(
        tags=[_TEAM_TAG],
        description="List the members of a team.",
        responses={
            200: TeamMemberListSerializer(many=True),
            401: None,
            404: None,
        },
    )
    def get(self, request: Request, event_id: int, team_id: int) -> Response:
        """Return the members of the requested team."""
        try:
            members = TeamMembershipService.list_members(event_id, team_id)
        except EventTeam.DoesNotExist:
            return _not_found(_TEAM_NOT_FOUND)
        return Response(
            TeamMemberListSerializer(members, many=True).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=[_TEAM_TAG],
        description="Add an event participant to a team.",
        request=TeamMemberCreateSerializer,
        responses={
            201: TeamMemberDetailSerializer,
            400: None,
            401: None,
            404: None,
            409: None,
        },
    )
    def post(self, request: Request, event_id: int, team_id: int) -> Response:
        """Add the player sent in the body to the team."""
        serializer = TeamMemberCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            membership = TeamMembershipService.add_member(
                event_id,
                team_id=team_id,
                player_id=serializer.validated_data["player_id"],
            )
        except EventTeam.DoesNotExist:
            return _not_found(_TEAM_NOT_FOUND)
        except PlayerNotFoundError:
            return Response(
                _PLAYER_NOT_FOUND_ERRORS, status=status.HTTP_400_BAD_REQUEST
            )
        except PlayerNotParticipantError:
            return _conflict("Player does not participate in this event.")
        except PlayerAlreadyInTeamError:
            return _conflict("Player already belongs to a team of this event.")
        return Response(
            TeamMemberDetailSerializer(membership).data,
            status=status.HTTP_201_CREATED,
        )


class TeamMemberDetailView(APIView):
    """Remove a member from a team."""

    @extend_schema(
        tags=[_TEAM_TAG],
        description="Remove a player from a team.",
        responses={204: None, 401: None, 404: None},
    )
    def delete(
        self, request: Request, event_id: int, team_id: int, player_id: int
    ) -> Response:
        """Remove the requested member."""
        try:
            TeamMembershipService.remove_member(
                event_id, team_id=team_id, player_id=player_id
            )
        except EventTeam.DoesNotExist:
            return _not_found(_TEAM_NOT_FOUND)
        except TeamMembership.DoesNotExist:
            return _not_found(_MEMBER_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class EventMatchListCreateView(APIView):
    """List and create the matches of an event."""

    @extend_schema(
        tags=[_MATCH_TAG],
        description="List the matches of an event.",
        responses={
            200: EventMatchListSerializer(many=True),
            401: None,
            404: None,
        },
    )
    def get(self, request: Request, event_id: int) -> Response:
        """Return the matches of the requested event."""
        try:
            matches = EventMatchService.list_matches(event_id)
        except Event.DoesNotExist:
            return _not_found(_EVENT_NOT_FOUND)
        return Response(
            EventMatchListSerializer(matches, many=True).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=[_MATCH_TAG],
        description="Create a match between two teams of the event.",
        request=EventMatchCreateSerializer,
        responses={
            201: EventMatchDetailSerializer,
            400: None,
            401: None,
            404: None,
        },
    )
    def post(self, request: Request, event_id: int) -> Response:
        """Create a match from the request body."""
        serializer = EventMatchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            match = EventMatchService.create_match(
                event_id, **_match_fields(serializer.validated_data)
            )
        except Event.DoesNotExist:
            return _not_found(_EVENT_NOT_FOUND)
        except TeamNotInEventError:
            return Response(
                {"detail": _TEAM_NOT_FOUND},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            EventMatchDetailSerializer(match).data,
            status=status.HTTP_201_CREATED,
        )


class EventMatchDetailView(APIView):
    """Retrieve, update and delete a match of an event."""

    @extend_schema(
        tags=[_MATCH_TAG],
        description="Retrieve a match of an event.",
        responses={200: EventMatchDetailSerializer, 401: None, 404: None},
    )
    def get(self, request: Request, event_id: int, match_id: int) -> Response:
        """Return the requested match."""
        try:
            match = EventMatchService.get_match(event_id, match_id)
        except EventMatch.DoesNotExist:
            return _not_found(_MATCH_NOT_FOUND)
        return Response(
            EventMatchDetailSerializer(match).data, status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=[_MATCH_TAG],
        description="Replace the data of a match.",
        request=EventMatchUpdateSerializer,
        responses={
            200: EventMatchDetailSerializer,
            400: None,
            401: None,
            404: None,
        },
    )
    def put(self, request: Request, event_id: int, match_id: int) -> Response:
        """Replace the data of the requested match."""
        serializer = EventMatchUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            match = EventMatchService.update_match(
                event_id,
                match_id,
                **_match_fields(serializer.validated_data),
            )
        except EventMatch.DoesNotExist:
            return _not_found(_MATCH_NOT_FOUND)
        except TeamNotInEventError:
            return Response(
                {"detail": _TEAM_NOT_FOUND},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            EventMatchDetailSerializer(match).data, status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=[_MATCH_TAG],
        description="Delete a match of an event.",
        responses={204: None, 401: None, 404: None},
    )
    def delete(
        self, request: Request, event_id: int, match_id: int
    ) -> Response:
        """Delete the requested match."""
        try:
            EventMatchService.delete_match(event_id, match_id)
        except EventMatch.DoesNotExist:
            return _not_found(_MATCH_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
