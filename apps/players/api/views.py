"""DRF API views for the players app."""

from typing import cast

from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param
from rest_framework.views import APIView

from apps.players.exceptions import (
    ActiveFormulaDeletionError,
    AttributeAbbreviationAlreadyExistsError,
    AttributeNameAlreadyExistsError,
    CardSlotTakenError,
    FormulaActivationError,
    FormulaError,
    PlayerAttributeAlreadyExistsError,
    PlayerEmailAlreadyExistsError,
    PlayerRoleAlreadyAssignedError,
)
from apps.players.models import (
    Attribute,
    OverallFormula,
    Player,
    PlayerAttribute,
    PlayerRole,
    Role,
)
from apps.players.serializers import (
    ActiveFormulaSerializer,
    AttributeCreateSerializer,
    AttributeDetailSerializer,
    AttributeListSerializer,
    AttributeUpdateSerializer,
    FormulaActivationErrorSerializer,
    FormulaPreviewRequestSerializer,
    FormulaPreviewSerializer,
    OverallFormulaCreateSerializer,
    OverallFormulaSerializer,
    PlayerAttributeCreateSerializer,
    PlayerAttributeDetailSerializer,
    PlayerAttributeListSerializer,
    PlayerAttributeUpdateSerializer,
    PlayerCardPageSerializer,
    PlayerCreateSerializer,
    PlayerDetailSerializer,
    PlayerListQuerySerializer,
    PlayerPhotoSerializer,
    PlayerRoleCreateSerializer,
    PlayerRoleSerializer,
    PlayerRoleUpdateSerializer,
    PlayerUpdateSerializer,
    RoleCreateSerializer,
    RoleDetailSerializer,
    RoleListSerializer,
    RoleUpdateSerializer,
)
from apps.players.services import (
    AttributeService,
    FormulaService,
    PlayerService,
)

_ROLE_TAG = "players-roles"
_PLAYER_TAG = "players"
_ATTRIBUTE_TAG = "players-attributes"
_ROLE_NOT_FOUND = {"detail": "Role not found."}
_PLAYER_NOT_FOUND = {"detail": "Player not found."}
_ROLE_NOT_ASSIGNED = {"detail": "Role not assigned to this player."}
_EMAIL_IN_USE = {"email": ["A player with this email already exists."]}
_ATTRIBUTE_NOT_FOUND = {"detail": "Attribute not found."}
_ATTRIBUTE_NAME_IN_USE = {
    "name": ["An attribute with this name already exists."]
}
_ATTRIBUTE_ABBREVIATION_IN_USE = {
    "abbreviation": ["An attribute with this abbreviation already exists."]
}
_CARD_SLOT_TAKEN = {
    "card_order": ["Another attribute already uses this card position."]
}
_RATING_NOT_FOUND = {"detail": "Player has no rating for this attribute."}
_FORMULA_TAG = "players-overall-formula"
_FORMULA_NOT_FOUND = {"detail": "Formula not found."}


def _formula_error(error: FormulaError) -> Response:
    """Build a 400 response for a script that cannot run.

    Args:
        error: Error raised by the formula engine.

    Returns:
        The 400 response naming the script field.
    """
    return Response(
        {"script": [error.message]}, status=status.HTTP_400_BAD_REQUEST
    )


def _not_found(body: dict[str, str]) -> Response:
    """Build a 404 response.

    Args:
        body: Error body returned to the client.

    Returns:
        The 404 response.
    """
    return Response(body, status=status.HTTP_404_NOT_FOUND)


def _conflict(body: dict[str, str] | dict[str, list[str]]) -> Response:
    """Build a 409 response.

    Args:
        body: Error body returned to the client.

    Returns:
        The 409 response.
    """
    return Response(body, status=status.HTTP_409_CONFLICT)


def _attribute_conflict(error: Exception) -> Response:
    """Translate an attribute uniqueness error into a 409 response.

    Args:
        error: Domain error raised by ``AttributeService``.

    Returns:
        The 409 response naming the conflicting field.
    """
    if isinstance(error, AttributeAbbreviationAlreadyExistsError):
        return _conflict(_ATTRIBUTE_ABBREVIATION_IN_USE)
    if isinstance(error, CardSlotTakenError):
        return _conflict(_CARD_SLOT_TAKEN)
    return _conflict(_ATTRIBUTE_NAME_IN_USE)


_ATTRIBUTE_CONFLICTS = (
    AttributeNameAlreadyExistsError,
    AttributeAbbreviationAlreadyExistsError,
    CardSlotTakenError,
)


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
        return Response(
            RoleListSerializer(roles, many=True).data,
            status=status.HTTP_200_OK,
        )

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
            return _not_found(_ROLE_NOT_FOUND)
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
            return _not_found(_ROLE_NOT_FOUND)
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
            return _not_found(_ROLE_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PlayerListCreateView(APIView):
    """List and create players."""

    @extend_schema(
        tags=[_PLAYER_TAG],
        description=(
            "List players as cards, paginated, with optional search by name, "
            "filter by role and ordering."
        ),
        operation_id="player_list",
        parameters=[PlayerListQuerySerializer],
        responses={200: PlayerCardPageSerializer, 400: None, 401: None},
    )
    def get(self, request: Request) -> Response:
        """Return one page of player cards."""
        query = PlayerListQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        page = query.validated_data["page"]
        page_size = query.validated_data["page_size"]
        result = PlayerService.list_player_cards(
            search=query.validated_data["search"],
            role_id=query.validated_data["role"],
            ordering=query.validated_data["ordering"],
            page=page,
            page_size=page_size,
        )
        current_url = request.build_absolute_uri()
        has_next = page * page_size < result.count
        body = {
            "count": result.count,
            "page": page,
            "page_size": page_size,
            "next": (
                replace_query_param(current_url, "page", page + 1)
                if has_next
                else None
            ),
            "previous": (
                replace_query_param(current_url, "page", page - 1)
                if page > 1
                else None
            ),
            "results": result.items,
        }
        return Response(
            PlayerCardPageSerializer(body).data, status=status.HTTP_200_OK
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
            return _conflict(_EMAIL_IN_USE)
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
            return _not_found(_PLAYER_NOT_FOUND)
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
            return _not_found(_PLAYER_NOT_FOUND)
        except PlayerEmailAlreadyExistsError:
            return _conflict(_EMAIL_IN_USE)
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
            return _not_found(_PLAYER_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PlayerPhotoView(APIView):
    """Upload and remove the photo of a player."""

    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        tags=[_PLAYER_TAG],
        description="Upload the photo of a player (JPEG, PNG or WEBP, 2 MB).",
        request={"multipart/form-data": PlayerPhotoSerializer},
        responses={
            200: PlayerDetailSerializer,
            400: None,
            401: None,
            404: None,
        },
    )
    def put(self, request: Request, player_id: int) -> Response:
        """Replace the photo of the requested player."""
        serializer = PlayerPhotoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            player = PlayerService.update_photo(
                player_id, serializer.validated_data["photo"]
            )
        except Player.DoesNotExist:
            return _not_found(_PLAYER_NOT_FOUND)
        return Response(
            PlayerDetailSerializer(player).data, status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=[_PLAYER_TAG],
        description="Remove the photo of a player.",
        responses={200: PlayerDetailSerializer, 401: None, 404: None},
    )
    def delete(self, request: Request, player_id: int) -> Response:
        """Remove the photo of the requested player."""
        try:
            player = PlayerService.remove_photo(player_id)
        except Player.DoesNotExist:
            return _not_found(_PLAYER_NOT_FOUND)
        return Response(
            PlayerDetailSerializer(player).data, status=status.HTTP_200_OK
        )


class PlayerRoleListCreateView(APIView):
    """List and assign the roles of a player."""

    @extend_schema(
        tags=[_PLAYER_TAG],
        description="List the roles of a player, primary first.",
        responses={
            200: PlayerRoleSerializer(many=True),
            401: None,
            404: None,
        },
    )
    def get(self, request: Request, player_id: int) -> Response:
        """Return the roles of the requested player."""
        try:
            roles = PlayerService.list_player_roles(player_id)
        except Player.DoesNotExist:
            return _not_found(_PLAYER_NOT_FOUND)
        return Response(
            PlayerRoleSerializer(roles, many=True).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=[_PLAYER_TAG],
        description=(
            "Assign a role to a player. The first role becomes the primary "
            "one."
        ),
        request=PlayerRoleCreateSerializer,
        responses={
            201: PlayerRoleSerializer,
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
            player_role = PlayerService.assign_role(
                player_id, serializer.validated_data["role_id"]
            )
        except Player.DoesNotExist:
            return _not_found(_PLAYER_NOT_FOUND)
        except Role.DoesNotExist:
            return Response(
                {"role_id": ["Role not found."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except PlayerRoleAlreadyAssignedError:
            return _conflict(
                {"detail": "Role already assigned to this player."}
            )
        return Response(
            PlayerRoleSerializer(player_role).data,
            status=status.HTTP_201_CREATED,
        )


class PlayerRoleDetailView(APIView):
    """Make primary or remove a role of a player."""

    @extend_schema(
        tags=[_PLAYER_TAG],
        description="Make the role the primary one of the player.",
        request=PlayerRoleUpdateSerializer,
        responses={
            200: PlayerRoleSerializer,
            400: None,
            401: None,
            404: None,
        },
    )
    def patch(
        self, request: Request, player_id: int, role_id: int
    ) -> Response:
        """Mark the role as the primary one."""
        serializer = PlayerRoleUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            player_role = PlayerService.set_primary_role(player_id, role_id)
        except PlayerRole.DoesNotExist:
            return _not_found(_ROLE_NOT_ASSIGNED)
        return Response(
            PlayerRoleSerializer(player_role).data, status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=[_PLAYER_TAG],
        description=(
            "Remove a role from a player. Removing the primary role promotes "
            "the oldest remaining one."
        ),
        responses={204: None, 401: None, 404: None},
    )
    def delete(
        self, request: Request, player_id: int, role_id: int
    ) -> Response:
        """Unassign the role from the player."""
        try:
            PlayerService.remove_role(player_id, role_id)
        except PlayerRole.DoesNotExist:
            return _not_found(_ROLE_NOT_ASSIGNED)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AttributeListCreateView(APIView):
    """List and create attributes of the catalog."""

    @extend_schema(
        tags=[_ATTRIBUTE_TAG],
        description="List all attributes.",
        responses={200: AttributeListSerializer(many=True), 401: None},
    )
    def get(self, request: Request) -> Response:
        """Return every attribute."""
        attributes = AttributeService.list_attributes()
        return Response(
            AttributeListSerializer(attributes, many=True).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=[_ATTRIBUTE_TAG],
        description=(
            "Create a new attribute. card_order (1 to 6) places it on the "
            "player cards; null keeps it off the cards."
        ),
        request=AttributeCreateSerializer,
        responses={
            201: AttributeDetailSerializer,
            400: None,
            401: None,
            409: None,
        },
    )
    def post(self, request: Request) -> Response:
        """Create an attribute from the request body."""
        serializer = AttributeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            attribute = AttributeService.create_attribute(
                **serializer.validated_data
            )
        except _ATTRIBUTE_CONFLICTS as error:
            return _attribute_conflict(error)
        return Response(
            AttributeDetailSerializer(attribute).data,
            status=status.HTTP_201_CREATED,
        )


class AttributeDetailView(APIView):
    """Retrieve, replace and delete an attribute."""

    @extend_schema(
        tags=[_ATTRIBUTE_TAG],
        description="Retrieve an attribute by ID.",
        responses={200: AttributeDetailSerializer, 401: None, 404: None},
    )
    def get(self, request: Request, attribute_id: int) -> Response:
        """Return the requested attribute."""
        try:
            attribute = AttributeService.get_attribute_by_id(attribute_id)
        except Attribute.DoesNotExist:
            return _not_found(_ATTRIBUTE_NOT_FOUND)
        return Response(
            AttributeDetailSerializer(attribute).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=[_ATTRIBUTE_TAG],
        description="Replace an attribute by ID.",
        request=AttributeUpdateSerializer,
        responses={
            200: AttributeDetailSerializer,
            400: None,
            401: None,
            404: None,
            409: None,
        },
    )
    def put(self, request: Request, attribute_id: int) -> Response:
        """Replace the data of the requested attribute."""
        serializer = AttributeUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            attribute = AttributeService.update_attribute(
                attribute_id, **serializer.validated_data
            )
        except Attribute.DoesNotExist:
            return _not_found(_ATTRIBUTE_NOT_FOUND)
        except _ATTRIBUTE_CONFLICTS as error:
            return _attribute_conflict(error)
        return Response(
            AttributeDetailSerializer(attribute).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=[_ATTRIBUTE_TAG],
        description="Delete an attribute and the ratings that use it.",
        responses={204: None, 401: None, 404: None},
    )
    def delete(self, request: Request, attribute_id: int) -> Response:
        """Delete the requested attribute."""
        try:
            AttributeService.delete_attribute(attribute_id)
        except Attribute.DoesNotExist:
            return _not_found(_ATTRIBUTE_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PlayerAttributeListCreateView(APIView):
    """List and create the ratings of a player."""

    @extend_schema(
        tags=[_PLAYER_TAG],
        description="List the attribute ratings of a player.",
        responses={
            200: PlayerAttributeListSerializer(many=True),
            401: None,
            404: None,
        },
    )
    def get(self, request: Request, player_id: int) -> Response:
        """Return the ratings of the requested player."""
        try:
            ratings = AttributeService.list_player_attributes(player_id)
        except Player.DoesNotExist:
            return _not_found(_PLAYER_NOT_FOUND)
        return Response(
            PlayerAttributeListSerializer(ratings, many=True).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=[_PLAYER_TAG],
        description="Rate a player in an attribute (0 to 100).",
        request=PlayerAttributeCreateSerializer,
        responses={
            201: PlayerAttributeDetailSerializer,
            400: None,
            401: None,
            404: None,
            409: None,
        },
    )
    def post(self, request: Request, player_id: int) -> Response:
        """Create the rating sent in the body."""
        serializer = PlayerAttributeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            rating = AttributeService.rate_player(
                player_id, **serializer.validated_data
            )
        except Player.DoesNotExist:
            return _not_found(_PLAYER_NOT_FOUND)
        except Attribute.DoesNotExist:
            return Response(
                {"attribute_id": ["Attribute not found."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except PlayerAttributeAlreadyExistsError:
            return _conflict(
                {"detail": "Player already has a rating for this attribute."}
            )
        return Response(
            PlayerAttributeDetailSerializer(rating).data,
            status=status.HTTP_201_CREATED,
        )


class PlayerAttributeDetailView(APIView):
    """Retrieve, update and remove a rating of a player."""

    @extend_schema(
        tags=[_PLAYER_TAG],
        description="Retrieve the rating of a player in an attribute.",
        responses={
            200: PlayerAttributeDetailSerializer,
            401: None,
            404: None,
        },
    )
    def get(
        self, request: Request, player_id: int, attribute_id: int
    ) -> Response:
        """Return the requested rating."""
        try:
            rating = AttributeService.get_rating(player_id, attribute_id)
        except PlayerAttribute.DoesNotExist:
            return _not_found(_RATING_NOT_FOUND)
        return Response(
            PlayerAttributeDetailSerializer(rating).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=[_PLAYER_TAG],
        description="Change the rating of a player in an attribute.",
        request=PlayerAttributeUpdateSerializer,
        responses={
            200: PlayerAttributeDetailSerializer,
            400: None,
            401: None,
            404: None,
        },
    )
    def put(
        self, request: Request, player_id: int, attribute_id: int
    ) -> Response:
        """Replace the value of the requested rating."""
        serializer = PlayerAttributeUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            rating = AttributeService.update_rating(
                player_id,
                attribute_id=attribute_id,
                value=serializer.validated_data["value"],
            )
        except PlayerAttribute.DoesNotExist:
            return _not_found(_RATING_NOT_FOUND)
        return Response(
            PlayerAttributeDetailSerializer(rating).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=[_PLAYER_TAG],
        description="Remove the rating of a player in an attribute.",
        responses={204: None, 401: None, 404: None},
    )
    def delete(
        self, request: Request, player_id: int, attribute_id: int
    ) -> Response:
        """Remove the requested rating."""
        try:
            AttributeService.remove_rating(player_id, attribute_id)
        except PlayerAttribute.DoesNotExist:
            return _not_found(_RATING_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class OverallFormulaListCreateView(APIView):
    """List and create versions of the overall formula."""

    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=[_FORMULA_TAG],
        description="List every formula version, newest first (staff only).",
        responses={
            200: OverallFormulaSerializer(many=True),
            401: None,
            403: None,
        },
    )
    def get(self, request: Request) -> Response:
        """Return every formula version."""
        return Response(
            OverallFormulaSerializer(
                FormulaService.list_formulas(), many=True
            ).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=[_FORMULA_TAG],
        description=(
            "Save a new, inactive formula version. The Lua script must "
            "define overall(notas, funcoes, principal) (staff only)."
        ),
        request=OverallFormulaCreateSerializer,
        responses={
            201: OverallFormulaSerializer,
            400: None,
            401: None,
            403: None,
        },
    )
    def post(self, request: Request) -> Response:
        """Create a formula version from the request body."""
        serializer = OverallFormulaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            formula = FormulaService.create_formula(
                **serializer.validated_data,
                author=cast(User, request.user),
            )
        except FormulaError as error:
            return _formula_error(error)
        return Response(
            OverallFormulaSerializer(formula).data,
            status=status.HTTP_201_CREATED,
        )


class OverallFormulaActiveView(APIView):
    """Show or stop the formula in use."""

    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=[_FORMULA_TAG],
        description=(
            "Return the formula in use; null means the simple average "
            "(staff only)."
        ),
        responses={200: ActiveFormulaSerializer, 401: None, 403: None},
    )
    def get(self, request: Request) -> Response:
        """Return the active formula."""
        return Response(
            ActiveFormulaSerializer(
                {"formula": FormulaService.get_active_formula()}
            ).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=[_FORMULA_TAG],
        description=(
            "Stop using formulas and recalculate every overall with the "
            "simple average (staff only)."
        ),
        responses={204: None, 401: None, 403: None},
    )
    def delete(self, request: Request) -> Response:
        """Go back to the simple average."""
        FormulaService.deactivate_formulas()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OverallFormulaPreviewView(APIView):
    """Test a script with real players without saving it."""

    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=[_FORMULA_TAG],
        description=(
            "Run a script for the first players by name and return the "
            "current and new overall of each one (staff only)."
        ),
        request=FormulaPreviewRequestSerializer,
        responses={
            200: FormulaPreviewSerializer(many=True),
            400: None,
            401: None,
            403: None,
        },
    )
    def post(self, request: Request) -> Response:
        """Return the preview of the script."""
        serializer = FormulaPreviewRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            results = FormulaService.preview(
                serializer.validated_data["script"],
                limit=serializer.validated_data["limit"],
            )
        except FormulaError as error:
            return _formula_error(error)
        return Response(
            FormulaPreviewSerializer(results, many=True).data,
            status=status.HTTP_200_OK,
        )


class OverallFormulaDetailView(APIView):
    """Retrieve and delete a formula version."""

    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=[_FORMULA_TAG],
        description="Retrieve a formula version (staff only).",
        responses={
            200: OverallFormulaSerializer,
            401: None,
            403: None,
            404: None,
        },
    )
    def get(self, request: Request, formula_id: int) -> Response:
        """Return the requested formula."""
        try:
            formula = FormulaService.get_formula(formula_id)
        except OverallFormula.DoesNotExist:
            return _not_found(_FORMULA_NOT_FOUND)
        return Response(
            OverallFormulaSerializer(formula).data, status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=[_FORMULA_TAG],
        description=(
            "Delete a formula version that is not in use (staff only)."
        ),
        responses={204: None, 401: None, 403: None, 404: None, 409: None},
    )
    def delete(self, request: Request, formula_id: int) -> Response:
        """Delete the requested formula."""
        try:
            FormulaService.delete_formula(formula_id)
        except OverallFormula.DoesNotExist:
            return _not_found(_FORMULA_NOT_FOUND)
        except ActiveFormulaDeletionError:
            return _conflict(
                {"detail": "Deactivate the formula before deleting it."}
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class OverallFormulaActivateView(APIView):
    """Activate a formula version."""

    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=[_FORMULA_TAG],
        description=(
            "Run the formula for every player and, when it works for all of "
            "them, make it the active one and store the new overalls "
            "(staff only)."
        ),
        request=None,
        responses={
            200: OverallFormulaSerializer,
            400: None,
            401: None,
            403: None,
            404: None,
            409: FormulaActivationErrorSerializer,
        },
    )
    def post(self, request: Request, formula_id: int) -> Response:
        """Activate the requested formula."""
        try:
            formula = FormulaService.activate_formula(formula_id)
        except OverallFormula.DoesNotExist:
            return _not_found(_FORMULA_NOT_FOUND)
        except FormulaError as error:
            return _formula_error(error)
        except FormulaActivationError as error:
            body = {
                "detail": "The formula failed for some players.",
                "failures": [
                    {"player_id": player_id, "player_name": name, "error": msg}
                    for player_id, name, msg in error.failures
                ],
            }
            return Response(
                FormulaActivationErrorSerializer(body).data,
                status=status.HTTP_409_CONFLICT,
            )
        return Response(
            OverallFormulaSerializer(formula).data, status=status.HTTP_200_OK
        )
