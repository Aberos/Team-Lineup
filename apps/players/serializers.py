"""Serializers for the players app."""

from datetime import date

from django.core.files.uploadedfile import UploadedFile
from django.core.validators import RegexValidator
from rest_framework import serializers

from apps.players.models import (
    ATTRIBUTE_ABBREVIATION_MAX_LENGTH,
    ATTRIBUTE_NAME_MAX_LENGTH,
    ATTRIBUTE_VALUE_MAX,
    ATTRIBUTE_VALUE_MIN,
    CARD_SLOT_MAX,
    CARD_SLOT_MIN,
    FORMULA_DESCRIPTION_MAX_LENGTH,
    PLAYER_EMAIL_MAX_LENGTH,
    PLAYER_NAME_MAX_LENGTH,
    PLAYER_PHONE_MAX_LENGTH,
    ROLE_NAME_MAX_LENGTH,
    Player,
    PlayerOrdering,
)
from apps.players.services import PlayerCard

PLAYER_NUMBER_MIN_VALUE = 0
PAGE_MIN = 1
PAGE_SIZE_DEFAULT = 24
PAGE_SIZE_MAX = 100
PHOTO_MAX_BYTES = 2 * 1024 * 1024
PHOTO_FORMATS = frozenset({"JPEG", "PNG", "WEBP"})
ABBREVIATION_PATTERN = r"^[A-Za-zÀ-ÖØ-öø-ÿ]+$"
FORMULA_SCRIPT_MAX_LENGTH = 10_000
PREVIEW_LIMIT_DEFAULT = 10
PREVIEW_LIMIT_MAX = 50


def _photo_url(player: Player) -> str | None:
    """Return the public URL of the player photo.

    Args:
        player: Player to read.

    Returns:
        The photo URL, or None when the player has no photo.
    """
    return player.photo.url if player.photo else None


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


class PlayerListQuerySerializer(serializers.Serializer):
    """Validate the query parameters of the player listing."""

    page = serializers.IntegerField(min_value=PAGE_MIN, default=PAGE_MIN)
    page_size = serializers.IntegerField(
        min_value=PAGE_MIN, max_value=PAGE_SIZE_MAX, default=PAGE_SIZE_DEFAULT
    )
    search = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    role = serializers.IntegerField(
        required=False, allow_null=True, default=None
    )
    ordering = serializers.ChoiceField(
        choices=PlayerOrdering.choices, default=PlayerOrdering.NAME
    )


class PlayerRoleSerializer(serializers.Serializer):
    """Format a role of a player."""

    id = serializers.IntegerField(source="role.id", read_only=True)
    name = serializers.CharField(source="role.name", read_only=True)
    is_primary = serializers.BooleanField(read_only=True)


class CardAttributeSerializer(serializers.Serializer):
    """Format a value shown on a player card."""

    abbreviation = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    value = serializers.IntegerField(read_only=True, allow_null=True)


class PlayerCardSerializer(serializers.Serializer):
    """Format the card of a player inside the listing."""

    id = serializers.IntegerField(source="player.id", read_only=True)
    name = serializers.CharField(source="player.name", read_only=True)
    number = serializers.IntegerField(source="player.number", read_only=True)
    overall = serializers.IntegerField(
        source="player.overall", read_only=True, allow_null=True
    )
    photo_url = serializers.SerializerMethodField()
    roles = PlayerRoleSerializer(many=True, read_only=True)
    card_attributes = CardAttributeSerializer(many=True, read_only=True)

    def get_photo_url(self, card: PlayerCard) -> str | None:
        """Return the photo URL of the card player.

        Args:
            card: Serialized card.

        Returns:
            The photo URL, or None when the player has no photo.
        """
        return _photo_url(card.player)


class PlayerCardPageSerializer(serializers.Serializer):
    """Format one page of the player listing."""

    count = serializers.IntegerField(read_only=True)
    page = serializers.IntegerField(read_only=True)
    page_size = serializers.IntegerField(read_only=True)
    next = serializers.URLField(read_only=True, allow_null=True)
    previous = serializers.URLField(read_only=True, allow_null=True)
    results = PlayerCardSerializer(many=True, read_only=True)


class PlayerDetailSerializer(serializers.Serializer):
    """Format a single player response."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    birthday = serializers.DateField(read_only=True)
    phone = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    number = serializers.IntegerField(read_only=True)
    overall = serializers.IntegerField(read_only=True, allow_null=True)
    photo_url = serializers.SerializerMethodField()

    def get_photo_url(self, player: Player) -> str | None:
        """Return the photo URL of the player.

        Args:
            player: Serialized player.

        Returns:
            The photo URL, or None when the player has no photo.
        """
        return _photo_url(player)


class PlayerPhotoSerializer(serializers.Serializer):
    """Validate an uploaded player photo."""

    photo = serializers.ImageField()

    def validate_photo(self, value: UploadedFile) -> UploadedFile:
        """Accept only JPEG, PNG or WEBP images up to 2 MB.

        Args:
            value: Uploaded image.

        Returns:
            The validated image.

        Raises:
            serializers.ValidationError: If the image is too large or of
                another format.
        """
        if (value.size or 0) > PHOTO_MAX_BYTES:
            raise serializers.ValidationError("Photo must be at most 2 MB.")
        image = getattr(value, "image", None)
        if getattr(image, "format", None) not in PHOTO_FORMATS:
            raise serializers.ValidationError(
                "Photo must be a JPEG, PNG or WEBP image."
            )
        return value


class PlayerRoleCreateSerializer(serializers.Serializer):
    """Validate the payload to assign a role to a player."""

    role_id = serializers.IntegerField()


class PlayerRoleUpdateSerializer(serializers.Serializer):
    """Validate the payload to make a role the primary one."""

    is_primary = serializers.BooleanField()

    def validate_is_primary(self, value: bool) -> bool:
        """Accept only true, since another role must become primary.

        Args:
            value: Requested flag.

        Returns:
            The validated flag.

        Raises:
            serializers.ValidationError: If the flag is false.
        """
        if not value:
            raise serializers.ValidationError(
                "Mark another role as primary instead."
            )
        return value


class AttributeCreateSerializer(serializers.Serializer):
    """Validate the payload to create an attribute."""

    name = serializers.CharField(max_length=ATTRIBUTE_NAME_MAX_LENGTH)
    abbreviation = serializers.CharField(
        max_length=ATTRIBUTE_ABBREVIATION_MAX_LENGTH,
        validators=[
            RegexValidator(
                ABBREVIATION_PATTERN, "Use only letters in the abbreviation."
            )
        ],
    )
    card_order = serializers.IntegerField(
        min_value=CARD_SLOT_MIN,
        max_value=CARD_SLOT_MAX,
        required=False,
        allow_null=True,
        default=None,
    )


class AttributeUpdateSerializer(AttributeCreateSerializer):
    """Validate the payload to replace an attribute."""


class AttributeListSerializer(serializers.Serializer):
    """Format an attribute inside a list response."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    abbreviation = serializers.CharField(read_only=True)
    card_order = serializers.IntegerField(read_only=True, allow_null=True)


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


class OverallFormulaCreateSerializer(serializers.Serializer):
    """Validate a new version of the overall formula."""

    script = serializers.CharField(
        max_length=FORMULA_SCRIPT_MAX_LENGTH, trim_whitespace=False
    )
    description = serializers.CharField(
        max_length=FORMULA_DESCRIPTION_MAX_LENGTH,
        required=False,
        allow_blank=True,
        default="",
    )


class OverallFormulaSerializer(serializers.Serializer):
    """Format a version of the overall formula."""

    id = serializers.IntegerField(read_only=True)
    script = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    created_by = serializers.CharField(
        source="created_by.username", read_only=True, allow_null=True
    )


class ActiveFormulaSerializer(serializers.Serializer):
    """Format the formula in use, or null for the simple average."""

    formula = OverallFormulaSerializer(read_only=True, allow_null=True)


class FormulaPreviewRequestSerializer(serializers.Serializer):
    """Validate a request to test a script with real players."""

    script = serializers.CharField(
        max_length=FORMULA_SCRIPT_MAX_LENGTH, trim_whitespace=False
    )
    limit = serializers.IntegerField(
        min_value=PAGE_MIN,
        max_value=PREVIEW_LIMIT_MAX,
        default=PREVIEW_LIMIT_DEFAULT,
    )


class FormulaPreviewSerializer(serializers.Serializer):
    """Format the result of a formula for one player."""

    player_id = serializers.IntegerField(read_only=True)
    player_name = serializers.CharField(read_only=True)
    current_overall = serializers.IntegerField(read_only=True, allow_null=True)
    new_overall = serializers.IntegerField(read_only=True, allow_null=True)
    error = serializers.CharField(read_only=True, allow_null=True)


class FormulaFailureSerializer(serializers.Serializer):
    """Format a player for which the formula failed."""

    player_id = serializers.IntegerField(read_only=True)
    player_name = serializers.CharField(read_only=True)
    error = serializers.CharField(read_only=True)


class FormulaActivationErrorSerializer(serializers.Serializer):
    """Format the players that prevented the activation."""

    detail = serializers.CharField(read_only=True)
    failures = FormulaFailureSerializer(many=True, read_only=True)
