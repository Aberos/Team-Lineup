"""Services for the players app."""

import logging
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

from django.contrib.auth.models import User
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

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
from apps.players.formula_engine import (
    CompiledFormula,
    FormulaInput,
    compile_formula,
)
from apps.players.models import (
    Attribute,
    OverallFormula,
    Player,
    PlayerAttribute,
    PlayerRole,
    Role,
)
from apps.players.repository import (
    AttributeRepository,
    OverallFormulaRepository,
    PlayerAttributeRepository,
    PlayerRepository,
    PlayerRoleRepository,
    RoleRepository,
)

ROUNDING_OFFSET = 0.5
MAX_REPORTED_FAILURES = 20

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DefaultAttribute:
    """Describe an attribute created by the default catalog seed.

    Attributes:
        name: Display name of the attribute.
        abbreviation: Short label shown on cards.
        card_order: Slot on the card.
    """

    name: str
    abbreviation: str
    card_order: int


DEFAULT_ROLE_NAMES: tuple[str, ...] = ("DEF", "MID", "ATK")
DEFAULT_ATTRIBUTES: tuple[DefaultAttribute, ...] = (
    DefaultAttribute("Velocidade", "VEL", 1),
    DefaultAttribute("Finalização", "FIN", 2),
    DefaultAttribute("Passe", "PAS", 3),
    DefaultAttribute("Drible", "DRI", 4),
    DefaultAttribute("Defesa", "DEF", 5),
    DefaultAttribute("Físico", "FÍS", 6),
)
DEFAULT_ATTRIBUTE_NAMES: tuple[str, ...] = tuple(
    attribute.name for attribute in DEFAULT_ATTRIBUTES
)


@dataclass(frozen=True)
class SeedResult:
    """Summarize the records created by the default catalog seed.

    Attributes:
        roles: Roles created by the seed.
        attributes: Attributes created by the seed.
    """

    roles: list[Role]
    attributes: list[Attribute]


@dataclass(frozen=True)
class CardAttributeValue:
    """Value of a player in one attribute shown on cards.

    Attributes:
        abbreviation: Short label of the attribute.
        name: Display name of the attribute.
        value: Rating of the player, or None when not rated.
    """

    abbreviation: str
    name: str
    value: int | None


@dataclass(frozen=True)
class PlayerCard:
    """Data needed to draw the card of a player.

    Attributes:
        player: The player.
        roles: Roles of the player, primary first.
        card_attributes: Values in the attributes shown on cards.
    """

    player: Player
    roles: list[PlayerRole]
    card_attributes: list[CardAttributeValue]


@dataclass(frozen=True)
class PlayerCardPage:
    """One page of player cards.

    Attributes:
        items: Cards of the page.
        count: Total of players that match the filters.
    """

    items: list[PlayerCard]
    count: int


class OverallService:
    """Business rules for the overall rating of players."""

    @staticmethod
    def calculate(values: Iterable[int]) -> int | None:
        """Return the rounded average of the card ratings.

        Args:
            values: Ratings of the player in attributes shown on cards.

        Returns:
            The overall rating, or None when there is no rating.
        """
        ratings = list(values)
        if not ratings:
            return None
        return int(sum(ratings) / len(ratings) + ROUNDING_OFFSET)

    @staticmethod
    def formula_input(player_id: int) -> FormulaInput:
        """Collect the data a formula receives for one player.

        Args:
            player_id: Primary key of the player.

        Returns:
            Card ratings by abbreviation, role names and primary role.
        """
        roles = PlayerRoleRepository.list_by_player(player_id)
        primary = next((item for item in roles if item.is_primary), None)
        return FormulaInput(
            ratings=PlayerAttributeRepository.card_ratings_by_abbreviation(
                player_id
            ),
            roles=[item.role.name for item in roles],
            primary=None if primary is None else primary.role.name,
        )

    @staticmethod
    def active_formula() -> CompiledFormula | None:
        """Compile the active formula, if any.

        Returns:
            The compiled formula, or None when the average is used or the
            stored script no longer compiles.
        """
        active = OverallFormulaRepository.get_active()
        if active is None:
            return None
        try:
            return compile_formula(active.script)
        except FormulaError as error:
            logger.warning(
                "Active overall formula %s does not compile: %s",
                active.id,
                error.message,
            )
            return None

    @staticmethod
    def compute(player_id: int, formula: CompiledFormula | None) -> int | None:
        """Calculate the overall of a player without storing it.

        Falls back to the average when the formula fails for the player.

        Args:
            player_id: Primary key of the player.
            formula: Compiled active formula, or None to use the average.

        Returns:
            The overall rating, or None when it cannot be computed.
        """
        data = OverallService.formula_input(player_id)
        if formula is not None:
            try:
                return formula.evaluate(data)
            except FormulaError as error:
                logger.warning(
                    "Overall formula failed for player %s: %s",
                    player_id,
                    error.message,
                )
        return OverallService.calculate(data.ratings.values())

    @staticmethod
    def refresh_player(player_id: int) -> int | None:
        """Recalculate and store the overall rating of a player.

        Args:
            player_id: Primary key of the player.

        Returns:
            The new overall rating.
        """
        overall = OverallService.compute(
            player_id, OverallService.active_formula()
        )
        PlayerRepository.update_overall(player_id, overall)
        return overall

    @staticmethod
    def refresh_players(player_ids: Iterable[int]) -> None:
        """Recalculate and store the overall rating of some players.

        Args:
            player_ids: Primary keys of the players.
        """
        formula = OverallService.active_formula()
        for player_id in player_ids:
            PlayerRepository.update_overall(
                player_id, OverallService.compute(player_id, formula)
            )

    @staticmethod
    def refresh_all() -> None:
        """Recalculate and store the overall rating of every player."""
        OverallService.refresh_players(PlayerRepository.list_ids())


class PlayerService:
    """Business rules for players and roles."""

    @staticmethod
    def seed_default_catalog(
        role_names: Iterable[str] = DEFAULT_ROLE_NAMES,
        attributes: Iterable[DefaultAttribute] = DEFAULT_ATTRIBUTES,
    ) -> SeedResult:
        """Create the default roles and attributes that do not exist yet.

        Names are compared without case, so running the seed again does not
        duplicate records. A default attribute only takes its card slot
        when the slot is free.

        Args:
            role_names: Names of the roles to guarantee.
            attributes: Attributes to guarantee.

        Returns:
            The roles and attributes created in this run.
        """
        with transaction.atomic():
            roles = [
                RoleRepository.create(name=name)
                for name in role_names
                if not RoleRepository.name_exists(name)
            ]
            created_attributes = [
                AttributeRepository.create(
                    name=attribute.name,
                    abbreviation=attribute.abbreviation,
                    card_order=(
                        None
                        if AttributeRepository.card_slot_taken(
                            attribute.card_order
                        )
                        else attribute.card_order
                    ),
                )
                for attribute in attributes
                if not AttributeRepository.name_exists(attribute.name)
            ]
        return SeedResult(roles=roles, attributes=created_attributes)

    @staticmethod
    def create_role(name: str) -> Role:
        """Create a role.

        Args:
            name: Display name of the role.

        Returns:
            The created role.
        """
        return RoleRepository.create(name=name.strip())

    @staticmethod
    def list_roles() -> list[Role]:
        """Return every role ordered by name."""
        return RoleRepository.list_all()

    @staticmethod
    def get_role_by_id(role_id: int) -> Role:
        """Return the role with the given identifier.

        Args:
            role_id: Primary key of the role.

        Returns:
            The matching role.

        Raises:
            Role.DoesNotExist: If the role does not exist.
        """
        return RoleRepository.get_by_id(role_id)

    @staticmethod
    def update_role(role_id: int, name: str) -> Role:
        """Rename an existing role.

        Args:
            role_id: Primary key of the role.
            name: New display name.

        Returns:
            The updated role.

        Raises:
            Role.DoesNotExist: If the role does not exist.
        """
        role = RoleRepository.get_by_id(role_id)
        with transaction.atomic():
            updated = RoleRepository.update_name(role, name=name.strip())
            OverallService.refresh_players(
                PlayerRoleRepository.players_with_role(role.id)
            )
        return updated

    @staticmethod
    def delete_role(role_id: int) -> None:
        """Delete an existing role and promote new primary roles.

        Players that had the deleted role as primary get their oldest
        remaining role as the new primary one.

        Args:
            role_id: Primary key of the role.

        Raises:
            Role.DoesNotExist: If the role does not exist.
        """
        role = RoleRepository.get_by_id(role_id)
        with transaction.atomic():
            promoted_players = PlayerRoleRepository.players_with_primary(
                role.id
            )
            affected_players = PlayerRoleRepository.players_with_role(role.id)
            RoleRepository.delete(role)
            for player_id in promoted_players:
                PlayerService._promote_oldest_role(player_id)
            OverallService.refresh_players(affected_players)

    @staticmethod
    def create_player(
        *,
        name: str,
        birthday: date,
        phone: str,
        email: str,
        number: int,
    ) -> Player:
        """Register a new player.

        Args:
            name: Full name of the player.
            birthday: Birth date of the player.
            phone: Contact phone number.
            email: Contact email, unique among players.
            number: Shirt number.

        Returns:
            The created player.

        Raises:
            PlayerEmailAlreadyExistsError: If the email is already in use.
        """
        normalized_email = email.strip().lower()
        if PlayerRepository.email_exists(normalized_email):
            raise PlayerEmailAlreadyExistsError
        return PlayerRepository.create(
            name=name.strip(),
            birthday=birthday,
            phone=phone.strip(),
            email=normalized_email,
            number=number,
        )

    @staticmethod
    def list_player_cards(
        *,
        search: str,
        role_id: int | None,
        ordering: str,
        page: int,
        page_size: int,
    ) -> PlayerCardPage:
        """Return one page of player cards.

        Args:
            search: Text that the player name must contain, ignoring case.
            role_id: Primary key of a role the player must have.
            ordering: Value of ``PlayerOrdering``.
            page: Page number, starting at 1.
            page_size: Number of cards per page.

        Returns:
            The cards of the page and the total of matching players.
        """
        players, count = PlayerRepository.search_page(
            search=search.strip(),
            role_id=role_id,
            ordering=ordering,
            offset=(page - 1) * page_size,
            limit=page_size,
        )
        card_attributes = AttributeRepository.list_card_attributes()
        cards = []
        for player in players:
            ratings = {
                rating.attribute_id: rating.value
                for rating in PlayerRepository.preloaded_card_ratings(player)
            }
            cards.append(
                PlayerCard(
                    player=player,
                    roles=PlayerRepository.preloaded_roles(player),
                    card_attributes=[
                        CardAttributeValue(
                            abbreviation=attribute.abbreviation,
                            name=attribute.name,
                            value=ratings.get(attribute.id),
                        )
                        for attribute in card_attributes
                    ],
                )
            )
        return PlayerCardPage(items=cards, count=count)

    @staticmethod
    def get_player_by_id(player_id: int) -> Player:
        """Return the player with the given identifier.

        Args:
            player_id: Primary key of the player.

        Returns:
            The matching player.

        Raises:
            Player.DoesNotExist: If the player does not exist.
        """
        return PlayerRepository.get_by_id(player_id)

    @staticmethod
    def update_player(
        player_id: int,
        *,
        name: str,
        birthday: date,
        phone: str,
        email: str,
        number: int,
    ) -> Player:
        """Replace the data of an existing player.

        Args:
            player_id: Primary key of the player.
            name: Full name of the player.
            birthday: Birth date of the player.
            phone: Contact phone number.
            email: Contact email, unique among players.
            number: Shirt number.

        Returns:
            The updated player.

        Raises:
            Player.DoesNotExist: If the player does not exist.
            PlayerEmailAlreadyExistsError: If another player uses the email.
        """
        player = PlayerRepository.get_by_id(player_id)
        normalized_email = email.strip().lower()
        if PlayerRepository.email_exists(
            normalized_email, exclude_id=player.id
        ):
            raise PlayerEmailAlreadyExistsError
        return PlayerRepository.update(
            player,
            name=name.strip(),
            birthday=birthday,
            phone=phone.strip(),
            email=normalized_email,
            number=number,
        )

    @staticmethod
    def update_photo(player_id: int, photo: UploadedFile) -> Player:
        """Replace the photo of a player.

        Args:
            player_id: Primary key of the player.
            photo: Validated image file.

        Returns:
            The updated player.

        Raises:
            Player.DoesNotExist: If the player does not exist.
        """
        player = PlayerRepository.get_by_id(player_id)
        return PlayerRepository.replace_photo(player, photo)

    @staticmethod
    def remove_photo(player_id: int) -> Player:
        """Remove the photo of a player.

        Args:
            player_id: Primary key of the player.

        Returns:
            The updated player.

        Raises:
            Player.DoesNotExist: If the player does not exist.
        """
        player = PlayerRepository.get_by_id(player_id)
        return PlayerRepository.remove_photo(player)

    @staticmethod
    def delete_player(player_id: int) -> None:
        """Delete an existing player.

        Args:
            player_id: Primary key of the player.

        Raises:
            Player.DoesNotExist: If the player does not exist.
        """
        player = PlayerRepository.get_by_id(player_id)
        PlayerRepository.delete(player)

    @staticmethod
    def list_player_roles(player_id: int) -> list[PlayerRole]:
        """Return the roles assigned to a player.

        Args:
            player_id: Primary key of the player.

        Returns:
            The roles of the player, primary first, then by name.

        Raises:
            Player.DoesNotExist: If the player does not exist.
        """
        player = PlayerRepository.get_by_id(player_id)
        return PlayerRoleRepository.list_by_player(player.id)

    @staticmethod
    def assign_role(player_id: int, role_id: int) -> PlayerRole:
        """Assign a role to a player.

        The first role of a player becomes the primary one.

        Args:
            player_id: Primary key of the player.
            role_id: Primary key of the role.

        Returns:
            The created relationship.

        Raises:
            Player.DoesNotExist: If the player does not exist.
            Role.DoesNotExist: If the role does not exist.
            PlayerRoleAlreadyAssignedError: If the player already has the
                role.
        """
        player = PlayerRepository.get_by_id(player_id)
        role = RoleRepository.get_by_id(role_id)
        if PlayerRoleRepository.exists(player.id, role.id):
            raise PlayerRoleAlreadyAssignedError
        with transaction.atomic():
            player_role = PlayerRoleRepository.create(
                player,
                role,
                is_primary=not PlayerRoleRepository.has_any(player.id),
            )
            OverallService.refresh_player(player.id)
        return player_role

    @staticmethod
    def set_primary_role(player_id: int, role_id: int) -> PlayerRole:
        """Make a role the primary one of the player.

        Args:
            player_id: Primary key of the player.
            role_id: Primary key of the role.

        Returns:
            The relationship marked as primary.

        Raises:
            PlayerRole.DoesNotExist: If the player does not have the role.
        """
        player_role = PlayerRoleRepository.get(player_id, role_id)
        with transaction.atomic():
            current = PlayerRoleRepository.get_primary(player_id)
            if current is not None and current.id != player_role.id:
                PlayerRoleRepository.set_primary(current, is_primary=False)
            updated = PlayerRoleRepository.set_primary(
                player_role, is_primary=True
            )
            OverallService.refresh_player(player_id)
        return updated

    @staticmethod
    def remove_role(player_id: int, role_id: int) -> None:
        """Remove a role from a player.

        When the primary role is removed, the oldest remaining role becomes
        the primary one.

        Args:
            player_id: Primary key of the player.
            role_id: Primary key of the role.

        Raises:
            PlayerRole.DoesNotExist: If the player does not have the role.
        """
        player_role = PlayerRoleRepository.get(player_id, role_id)
        with transaction.atomic():
            PlayerRoleRepository.delete(player_role)
            if player_role.is_primary:
                PlayerService._promote_oldest_role(player_id)
            OverallService.refresh_player(player_id)

    @staticmethod
    def _promote_oldest_role(player_id: int) -> None:
        """Mark the oldest role of the player as primary, if any.

        Args:
            player_id: Primary key of the player.
        """
        oldest = PlayerRoleRepository.first_assigned(player_id)
        if oldest is not None:
            PlayerRoleRepository.set_primary(oldest, is_primary=True)


class AttributeService:
    """Business rules for the attribute catalog and player ratings."""

    @staticmethod
    def _ensure_unique(
        *,
        name: str,
        abbreviation: str,
        card_order: int | None,
        exclude_id: int | None = None,
    ) -> None:
        """Reject a name, abbreviation or card slot already in use.

        Args:
            name: Normalized name.
            abbreviation: Normalized abbreviation.
            card_order: Requested card slot.
            exclude_id: Primary key of the attribute being updated.

        Raises:
            AttributeNameAlreadyExistsError: If the name is in use.
            AttributeAbbreviationAlreadyExistsError: If the abbreviation is
                in use.
            CardSlotTakenError: If the card slot is taken.
        """
        if AttributeRepository.name_exists(name, exclude_id=exclude_id):
            raise AttributeNameAlreadyExistsError
        if AttributeRepository.abbreviation_exists(
            abbreviation, exclude_id=exclude_id
        ):
            raise AttributeAbbreviationAlreadyExistsError
        if card_order is not None and AttributeRepository.card_slot_taken(
            card_order, exclude_id=exclude_id
        ):
            raise CardSlotTakenError

    @staticmethod
    def create_attribute(
        *, name: str, abbreviation: str, card_order: int | None
    ) -> Attribute:
        """Create an attribute.

        Args:
            name: Display name, unique without case.
            abbreviation: Short label for cards, unique without case.
            card_order: Free card slot, or None when not shown on cards.

        Returns:
            The created attribute.

        Raises:
            AttributeNameAlreadyExistsError: If the name is in use.
            AttributeAbbreviationAlreadyExistsError: If the abbreviation is
                in use.
            CardSlotTakenError: If the card slot is taken.
        """
        normalized_name = name.strip()
        normalized_abbreviation = abbreviation.strip().upper()
        AttributeService._ensure_unique(
            name=normalized_name,
            abbreviation=normalized_abbreviation,
            card_order=card_order,
        )
        return AttributeRepository.create(
            name=normalized_name,
            abbreviation=normalized_abbreviation,
            card_order=card_order,
        )

    @staticmethod
    def list_attributes() -> list[Attribute]:
        """Return every attribute ordered by name."""
        return AttributeRepository.list_all()

    @staticmethod
    def get_attribute_by_id(attribute_id: int) -> Attribute:
        """Return the attribute with the given identifier.

        Args:
            attribute_id: Primary key of the attribute.

        Returns:
            The matching attribute.

        Raises:
            Attribute.DoesNotExist: If the attribute does not exist.
        """
        return AttributeRepository.get_by_id(attribute_id)

    @staticmethod
    def update_attribute(
        attribute_id: int,
        *,
        name: str,
        abbreviation: str,
        card_order: int | None,
    ) -> Attribute:
        """Replace the data of an attribute.

        Changing the card slot recalculates the overall of every player.

        Args:
            attribute_id: Primary key of the attribute.
            name: New display name, unique without case.
            abbreviation: New short label, unique without case.
            card_order: Free card slot, or None to hide it from cards.

        Returns:
            The updated attribute.

        Raises:
            Attribute.DoesNotExist: If the attribute does not exist.
            AttributeNameAlreadyExistsError: If another attribute uses the
                name.
            AttributeAbbreviationAlreadyExistsError: If another attribute
                uses the abbreviation.
            CardSlotTakenError: If another attribute occupies the slot.
        """
        attribute = AttributeRepository.get_by_id(attribute_id)
        normalized_name = name.strip()
        normalized_abbreviation = abbreviation.strip().upper()
        AttributeService._ensure_unique(
            name=normalized_name,
            abbreviation=normalized_abbreviation,
            card_order=card_order,
            exclude_id=attribute.id,
        )
        card_visibility_changed = (attribute.card_order is None) != (
            card_order is None
        )
        with transaction.atomic():
            updated = AttributeRepository.update(
                attribute,
                name=normalized_name,
                abbreviation=normalized_abbreviation,
                card_order=card_order,
            )
            if card_visibility_changed:
                OverallService.refresh_all()
        return updated

    @staticmethod
    def delete_attribute(attribute_id: int) -> None:
        """Delete an attribute and the ratings that use it.

        Deleting an attribute shown on cards recalculates every overall.

        Args:
            attribute_id: Primary key of the attribute.

        Raises:
            Attribute.DoesNotExist: If the attribute does not exist.
        """
        attribute = AttributeRepository.get_by_id(attribute_id)
        was_on_card = attribute.card_order is not None
        with transaction.atomic():
            AttributeRepository.delete(attribute)
            if was_on_card:
                OverallService.refresh_all()

    @staticmethod
    def list_player_attributes(player_id: int) -> list[PlayerAttribute]:
        """Return the ratings of a player.

        Args:
            player_id: Primary key of the player.

        Returns:
            The ratings ordered by attribute name.

        Raises:
            Player.DoesNotExist: If the player does not exist.
        """
        player = PlayerRepository.get_by_id(player_id)
        return PlayerAttributeRepository.list_by_player(player.id)

    @staticmethod
    def rate_player(
        player_id: int, *, attribute_id: int, value: int
    ) -> PlayerAttribute:
        """Give a player a rating in an attribute.

        Args:
            player_id: Primary key of the player.
            attribute_id: Primary key of the attribute.
            value: Rating between the allowed bounds.

        Returns:
            The created rating.

        Raises:
            Player.DoesNotExist: If the player does not exist.
            Attribute.DoesNotExist: If the attribute does not exist.
            PlayerAttributeAlreadyExistsError: If the player already has a
                rating for the attribute.
        """
        player = PlayerRepository.get_by_id(player_id)
        attribute = AttributeRepository.get_by_id(attribute_id)
        if PlayerAttributeRepository.exists(player.id, attribute.id):
            raise PlayerAttributeAlreadyExistsError
        with transaction.atomic():
            rating = PlayerAttributeRepository.create(
                player=player, attribute=attribute, value=value
            )
            OverallService.refresh_player(player.id)
        return rating

    @staticmethod
    def get_rating(player_id: int, attribute_id: int) -> PlayerAttribute:
        """Return the rating of a player in an attribute.

        Args:
            player_id: Primary key of the player.
            attribute_id: Primary key of the attribute.

        Returns:
            The matching rating.

        Raises:
            PlayerAttribute.DoesNotExist: If the player has no rating for
                the attribute.
        """
        return PlayerAttributeRepository.get(player_id, attribute_id)

    @staticmethod
    def update_rating(
        player_id: int, *, attribute_id: int, value: int
    ) -> PlayerAttribute:
        """Change the rating of a player in an attribute.

        Args:
            player_id: Primary key of the player.
            attribute_id: Primary key of the attribute.
            value: New rating between the allowed bounds.

        Returns:
            The updated rating.

        Raises:
            PlayerAttribute.DoesNotExist: If the player has no rating for
                the attribute.
        """
        player_attribute = PlayerAttributeRepository.get(
            player_id, attribute_id
        )
        with transaction.atomic():
            rating = PlayerAttributeRepository.update_value(
                player_attribute, value=value
            )
            OverallService.refresh_player(player_id)
        return rating

    @staticmethod
    def remove_rating(player_id: int, attribute_id: int) -> None:
        """Remove the rating of a player in an attribute.

        Args:
            player_id: Primary key of the player.
            attribute_id: Primary key of the attribute.

        Raises:
            PlayerAttribute.DoesNotExist: If the player has no rating for
                the attribute.
        """
        player_attribute = PlayerAttributeRepository.get(
            player_id, attribute_id
        )
        with transaction.atomic():
            PlayerAttributeRepository.delete(player_attribute)
            OverallService.refresh_player(player_id)


@dataclass(frozen=True)
class FormulaPreview:
    """Result of a formula for one player, before activating it.

    Attributes:
        player_id: Primary key of the player.
        player_name: Name of the player.
        current_overall: Overall stored for the player.
        new_overall: Overall returned by the formula.
        error: Error message when the formula failed for the player.
    """

    player_id: int
    player_name: str
    current_overall: int | None
    new_overall: int | None
    error: str | None


class FormulaService:
    """Business rules for the versions of the overall formula."""

    @staticmethod
    def list_formulas() -> list[OverallFormula]:
        """Return every formula version, newest first."""
        return OverallFormulaRepository.list_all()

    @staticmethod
    def get_formula(formula_id: int) -> OverallFormula:
        """Return a formula version.

        Args:
            formula_id: Primary key of the formula.

        Returns:
            The matching formula.

        Raises:
            OverallFormula.DoesNotExist: If the formula does not exist.
        """
        return OverallFormulaRepository.get_by_id(formula_id)

    @staticmethod
    def get_active_formula() -> OverallFormula | None:
        """Return the formula in use, or None when the average is used."""
        return OverallFormulaRepository.get_active()

    @staticmethod
    def create_formula(
        *, script: str, description: str, author: User | None
    ) -> OverallFormula:
        """Save a new formula version after checking that it compiles.

        Args:
            script: Lua source that defines ``overall``.
            description: Short note about the version.
            author: User that wrote the version.

        Returns:
            The created, inactive formula.

        Raises:
            FormulaError: If the script does not compile.
        """
        compile_formula(script)
        return OverallFormulaRepository.create(
            script=script,
            description=description.strip(),
            created_by=author,
        )

    @staticmethod
    def preview(script: str, *, limit: int) -> list[FormulaPreview]:
        """Run a script for some players without storing anything.

        Args:
            script: Lua source that defines ``overall``.
            limit: Maximum number of players, ordered by name.

        Returns:
            The current and new overall of each player.

        Raises:
            FormulaError: If the script does not compile.
        """
        formula = compile_formula(script)
        results = []
        for player in PlayerRepository.list_by_name(limit):
            new_overall: int | None = None
            error: str | None = None
            try:
                new_overall = formula.evaluate(
                    OverallService.formula_input(player.id)
                )
            except FormulaError as failure:
                error = failure.message
            results.append(
                FormulaPreview(
                    player_id=player.id,
                    player_name=player.name,
                    current_overall=player.overall,
                    new_overall=new_overall,
                    error=error,
                )
            )
        return results

    @staticmethod
    def activate_formula(formula_id: int) -> OverallFormula:
        """Activate a formula and recalculate every overall with it.

        The formula is first run for every player; nothing changes if it
        fails for any of them.

        Args:
            formula_id: Primary key of the formula.

        Returns:
            The activated formula.

        Raises:
            OverallFormula.DoesNotExist: If the formula does not exist.
            FormulaError: If the stored script no longer compiles.
            FormulaActivationError: If the formula fails for some players.
        """
        formula = OverallFormulaRepository.get_by_id(formula_id)
        compiled = compile_formula(formula.script)
        overalls: dict[int, int | None] = {}
        failures: list[tuple[int, str, str]] = []
        for player in PlayerRepository.list_by_name():
            try:
                overalls[player.id] = compiled.evaluate(
                    OverallService.formula_input(player.id)
                )
            except FormulaError as failure:
                failures.append((player.id, player.name, failure.message))
        if failures:
            raise FormulaActivationError(failures[:MAX_REPORTED_FAILURES])
        with transaction.atomic():
            activated = OverallFormulaRepository.activate(formula)
            for player_id, overall in overalls.items():
                PlayerRepository.update_overall(player_id, overall)
        return activated

    @staticmethod
    def deactivate_formulas() -> None:
        """Stop using formulas and go back to the simple average."""
        with transaction.atomic():
            OverallFormulaRepository.deactivate_all()
            OverallService.refresh_all()

    @staticmethod
    def delete_formula(formula_id: int) -> None:
        """Delete a formula version that is not in use.

        Args:
            formula_id: Primary key of the formula.

        Raises:
            OverallFormula.DoesNotExist: If the formula does not exist.
            ActiveFormulaDeletionError: If the formula is the active one.
        """
        formula = OverallFormulaRepository.get_by_id(formula_id)
        if formula.is_active:
            raise ActiveFormulaDeletionError
        OverallFormulaRepository.delete(formula)
