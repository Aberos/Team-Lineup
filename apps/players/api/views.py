"""DRF API views for the players app."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.players.exceptions import (
    PlayerEmailAlreadyExistsError,
    PlayerRoleAlreadyAssignedError,
)
from apps.players.models import Player, PlayerRole, Role
from apps.players.serializers import (
    PlayerCreateSerializer,
    PlayerDetailSerializer,
    PlayerListSerializer,
    PlayerRoleCreateSerializer,
    PlayerUpdateSerializer,
    RoleCreateSerializer,
    RoleDetailSerializer,
    RoleListSerializer,
    RoleUpdateSerializer,
)
from apps.players.services import PlayerService

_ROLE_TAG = "players-roles"
_PLAYER_TAG = "players"
_ROLE_NOT_FOUND = {"detail": "Role not found."}
_PLAYER_NOT_FOUND = {"detail": "Player not found."}
_EMAIL_IN_USE = {"email": ["A player with this email already exists."]}


class RoleListCreateView(APIView):
    """List and create player roles."""

    @extend_schema(
        tags=[_ROLE_TAG],
        description="List all roles.",
        responses={200: RoleListSerializer(many=True), 401: None},
    )
    def get(self, request: Request) -> Response:
        """Return every role."""
        roles = PlayerService.list_roles()
        serializer = RoleListSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=[_ROLE_TAG],
        description="Create a new role.",
        request=RoleCreateSerializer,
        responses={201: RoleDetailSerializer, 400: None, 401: None},
    )
    def post(self, request: Request) -> Response:
        """Create a role from the request body."""
        serializer = RoleCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = PlayerService.create_role(
            name=serializer.validated_data["name"]
        )
        return Response(
            RoleDetailSerializer(role).data,
            status=status.HTTP_201_CREATED,
        )


class RoleDetailView(APIView):
    """Retrieve, update and delete a player role."""

    @extend_schema(
        tags=[_ROLE_TAG],
        description="Retrieve a role by ID.",
        responses={200: RoleDetailSerializer, 401: None, 404: None},
    )
    def get(self, request: Request, role_id: int) -> Response:
        """Return the requested role."""
        try:
            role = PlayerService.get_role_by_id(role_id)
        except Role.DoesNotExist:
            return Response(_ROLE_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
        return Response(
            RoleDetailSerializer(role).data, status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=[_ROLE_TAG],
        description="Update a role by ID.",
        request=RoleUpdateSerializer,
        responses={
            200: RoleDetailSerializer,
            400: None,
            401: None,
            404: None,
        },
    )
    def put(self, request: Request, role_id: int) -> Response:
        """Replace the data of the requested role."""
        serializer = RoleUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            role = PlayerService.update_role(
                role_id, name=serializer.validated_data["name"]
            )
        except Role.DoesNotExist:
            return Response(_ROLE_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
        return Response(
            RoleDetailSerializer(role).data, status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=[_ROLE_TAG],
        description="Delete a role by ID.",
        responses={204: None, 401: None, 404: None},
    )
    def delete(self, request: Request, role_id: int) -> Response:
        """Delete the requested role."""
        try:
            PlayerService.delete_role(role_id)
        except Role.DoesNotExist:
            return Response(_ROLE_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PlayerListCreateView(APIView):
    """List and create players."""

    @extend_schema(
        tags=[_PLAYER_TAG],
        description="List all players.",
        responses={200: PlayerListSerializer(many=True), 401: None},
    )
    def get(self, request: Request) -> Response:
        """Return every player."""
        players = PlayerService.list_players()
        return Response(
            PlayerListSerializer(players, many=True).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=[_PLAYER_TAG],
        description="Register a new player.",
        request=PlayerCreateSerializer,
        responses={
            201: PlayerDetailSerializer,
            400: None,
            401: None,
            409: None,
        },
    )
    def post(self, request: Request) -> Response:
        """Create a player from the request body."""
        serializer = PlayerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            player = PlayerService.create_player(**serializer.validated_data)
        except PlayerEmailAlreadyExistsError:
            return Response(_EMAIL_IN_USE, status=status.HTTP_409_CONFLICT)
        return Response(
            PlayerDetailSerializer(player).data,
            status=status.HTTP_201_CREATED,
        )


class PlayerDetailView(APIView):
    """Retrieve, update and delete a player."""

    @extend_schema(
        tags=[_PLAYER_TAG],
        description="Retrieve a player by ID.",
        responses={200: PlayerDetailSerializer, 401: None, 404: None},
    )
    def get(self, request: Request, player_id: int) -> Response:
        """Return the requested player."""
        try:
            player = PlayerService.get_player_by_id(player_id)
        except Player.DoesNotExist:
            return Response(
                _PLAYER_NOT_FOUND, status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            PlayerDetailSerializer(player).data, status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=[_PLAYER_TAG],
        description="Replace the data of a player by ID.",
        request=PlayerUpdateSerializer,
        responses={
            200: PlayerDetailSerializer,
            400: None,
            401: None,
            404: None,
            409: None,
        },
    )
    def put(self, request: Request, player_id: int) -> Response:
        """Replace the data of the requested player."""
        serializer = PlayerUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            player = PlayerService.update_player(
                player_id, **serializer.validated_data
            )
        except Player.DoesNotExist:
            return Response(
                _PLAYER_NOT_FOUND, status=status.HTTP_404_NOT_FOUND
            )
        except PlayerEmailAlreadyExistsError:
            return Response(_EMAIL_IN_USE, status=status.HTTP_409_CONFLICT)
        return Response(
            PlayerDetailSerializer(player).data, status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=[_PLAYER_TAG],
        description="Delete a player by ID.",
        responses={204: None, 401: None, 404: None},
    )
    def delete(self, request: Request, player_id: int) -> Response:
        """Delete the requested player."""
        try:
            PlayerService.delete_player(player_id)
        except Player.DoesNotExist:
            return Response(
                _PLAYER_NOT_FOUND, status=status.HTTP_404_NOT_FOUND
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class PlayerRoleListCreateView(APIView):
    """List and assign the roles of a player."""

    @extend_schema(
        tags=[_PLAYER_TAG],
        description="List the roles assigned to a player.",
        responses={
            200: RoleListSerializer(many=True),
            401: None,
            404: None,
        },
    )
    def get(self, request: Request, player_id: int) -> Response:
        """Return the roles of the requested player."""
        try:
            roles = PlayerService.list_player_roles(player_id)
        except Player.DoesNotExist:
            return Response(
                _PLAYER_NOT_FOUND, status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            RoleListSerializer(roles, many=True).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=[_PLAYER_TAG],
        description="Assign a role to a player.",
        request=PlayerRoleCreateSerializer,
        responses={
            201: RoleDetailSerializer,
            400: None,
            401: None,
            404: None,
            409: None,
        },
    )
    def post(self, request: Request, player_id: int) -> Response:
        """Assign the role sent in the body to the player."""
        serializer = PlayerRoleCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            role = PlayerService.assign_role(
                player_id, serializer.validated_data["role_id"]
            )
        except Player.DoesNotExist:
            return Response(
                _PLAYER_NOT_FOUND, status=status.HTTP_404_NOT_FOUND
            )
        except Role.DoesNotExist:
            return Response(
                {"role_id": ["Role not found."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except PlayerRoleAlreadyAssignedError:
            return Response(
                {"detail": "Role already assigned to this player."},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(
            RoleDetailSerializer(role).data, status=status.HTTP_201_CREATED
        )


class PlayerRoleDetailView(APIView):
    """Remove a role from a player."""

    @extend_schema(
        tags=[_PLAYER_TAG],
        description="Remove a role from a player.",
        responses={204: None, 401: None, 404: None},
    )
    def delete(
        self, request: Request, player_id: int, role_id: int
    ) -> Response:
        """Unassign the role from the player."""
        try:
            PlayerService.remove_role(player_id, role_id)
        except PlayerRole.DoesNotExist:
            return Response(
                {"detail": "Role not assigned to this player."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
