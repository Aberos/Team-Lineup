"""Views for the players app."""

from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.players.models import Role
from apps.players.serializers import (
    RoleCreateSerializer,
    RoleDetailSerializer,
    RoleListSerializer,
    RoleUpdateSerializer,
)
from apps.players.services import PlayerService


@extend_schema(
    description="Create a new role.",
    request=RoleCreateSerializer,
    responses={201: None},
)
class RoleCreateView(APIView):
    """View for creating a new role."""

    def post(self, request: Request) -> Response:
        """Handle POST request to create a new role."""
        serializer = RoleCreateSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=400)

        PlayerService.create_role(name=serializer.validated_data["name"])
        return Response(status=201)


@extend_schema(
    description="List all roles.",
    responses={200: RoleListSerializer(many=True)},
)
class RoleListView(APIView):
    """View for listing all roles."""

    def get(self, request: Request) -> Response:
        """Handle GET request to list all roles."""
        roles = PlayerService.list_roles()
        serializer = RoleListSerializer(roles, many=True)
        return Response(serializer.data, status=200)


@extend_schema(
    description="Retrieve a specific role by ID.",
    responses={200: RoleDetailSerializer, 404: None},
)
class RoleDetailView(APIView):
    """View for retrieving a specific role by ID."""

    def get(self, request: Request, role_id: int) -> Response:
        """Handle GET request to retrieve a specific role."""
        try:
            role = PlayerService.get_role_by_id(role_id)
        except Role.DoesNotExist:
            return Response({"detail": "Role not found."}, status=404)

        serializer = RoleDetailSerializer(role)
        return Response(serializer.data, status=200)


@extend_schema(
    description="Delete a specific role by ID.",
    responses={204: None, 404: None},
)
class RoleDeleteView(APIView):
    """View for deleting a specific role by ID."""

    def delete(self, request: Request, role_id: int) -> Response:
        """Handle DELETE request to delete a specific role."""
        try:
            PlayerService.delete_role(role_id)
        except Role.DoesNotExist:
            return Response({"detail": "Role not found."}, status=404)
        return Response(status=204)


@extend_schema(
    description="Update a specific role by ID.",
    request=RoleUpdateSerializer,
    responses={200: RoleDetailSerializer, 404: None},
)
class RoleUpdateView(APIView):
    """View for updating a specific role by ID."""

    def put(self, request: Request, role_id: int) -> Response:
        """Handle PUT request to update a specific role."""
        serializer = RoleUpdateSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=400)
        try:
            role = PlayerService.update_role(
                role_id, name=serializer.validated_data["name"]
            )
        except Role.DoesNotExist:
            return Response({"detail": "Role not found."}, status=404)

        response_serializer = RoleDetailSerializer(role)
        return Response(response_serializer.data, status=200)
