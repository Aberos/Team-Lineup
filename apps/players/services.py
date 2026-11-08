"""Services for the players app."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

from django.db import transaction

from apps.players.exceptions import (
    AttributeNameAlreadyExistsError,
    PlayerAttributeAlreadyExistsError,
    PlayerEmailAlreadyExistsError,
    PlayerRoleAlreadyAssignedError,
)
from apps.players.models import Attribute, Player, PlayerAttribute, Role
from apps.players.repository import (
    AttributeRepository,
    PlayerAttributeRepository,
    PlayerRepository,
    PlayerRoleRepository,
    RoleRepository,
)

DEFAULT_ROLE_NAMES: tuple[str, ...] = ("DEF", "MID", "ATK")
DEFAULT_ATTRIBUTE_NAMES: tuple[str, ...] = (
    "Velocidade",
    "Passe",
    "Finalização",
    "Drible",
    "Defesa",
    "Físico",
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


class PlayerService:
    """Business rules for players and roles."""

    @staticmethod
    def seed_default_catalog(
        role_names: Iterable[str] = DEFAULT_ROLE_NAMES,
        attribute_names: Iterable[str] = DEFAULT_ATTRIBUTE_NAMES,
    ) -> SeedResult:
        """Create the default roles and attributes that do not exist yet.

        Names are compared without case, so running the seed again does not
        duplicate records.

        Args:
            role_names: Names of the roles to guarantee.
            attribute_names: Names of the attributes to guarantee.

        Returns:
            The roles and attributes created in this run.
        """
        with transaction.atomic():
            roles = [
                RoleRepository.create(name=name)
                for name in role_names
                if not RoleRepository.name_exists(name)
            ]
            attributes = [
                AttributeRepository.create(name=name)
                for name in attribute_names
                if not AttributeRepository.name_exists(name)
            ]
        return SeedResult(roles=roles, attributes=attributes)

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
        return RoleRepository.update_name(role, name=name.strip())

    @staticmethod
    def delete_role(role_id: int) -> None:
        """Delete an existing role.

        Args:
            role_id: Primary key of the role.

        Raises:
            Role.DoesNotExist: If the role does not exist.
        """
        role = RoleRepository.get_by_id(role_id)
        RoleRepository.delete(role)

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
    def list_players() -> list[Player]:
        """Return every player ordered by name."""
        return PlayerRepository.list_all()

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
    def list_player_roles(player_id: int) -> list[Role]:
        """Return the roles assigned to a player.

        Args:
            player_id: Primary key of the player.

        Returns:
            The roles of the player ordered by name.

        Raises:
            Player.DoesNotExist: If the player does not exist.
        """
        player = PlayerRepository.get_by_id(player_id)
        return RoleRepository.list_by_player(player.id)

    @staticmethod
    def assign_role(player_id: int, role_id: int) -> Role:
        """Assign a role to a player.

        Args:
            player_id: Primary key of the player.
            role_id: Primary key of the role.

        Returns:
            The assigned role.

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
        PlayerRoleRepository.create(player=player, role=role)
        return role

    @staticmethod
    def remove_role(player_id: int, role_id: int) -> None:
        """Remove a role from a player.

        Args:
            player_id: Primary key of the player.
            role_id: Primary key of the role.

        Raises:
            PlayerRole.DoesNotExist: If the player does not have the role.
        """
        player_role = PlayerRoleRepository.get(player_id, role_id)
        PlayerRoleRepository.delete(player_role)


class AttributeService:
    """Business rules for the attribute catalog and player ratings."""

    @staticmethod
    def create_attribute(name: str) -> Attribute:
        """Create an attribute.

        Args:
            name: Display name, unique without case.

        Returns:
            The created attribute.

        Raises:
            AttributeNameAlreadyExistsError: If the name is already in use.
        """
        normalized_name = name.strip()
        if AttributeRepository.name_exists(normalized_name):
            raise AttributeNameAlreadyExistsError
        return AttributeRepository.create(name=normalized_name)

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
    def rename_attribute(attribute_id: int, name: str) -> Attribute:
        """Rename an attribute.

        Args:
            attribute_id: Primary key of the attribute.
            name: New display name, unique without case.

        Returns:
            The updated attribute.

        Raises:
            Attribute.DoesNotExist: If the attribute does not exist.
            AttributeNameAlreadyExistsError: If another attribute uses the
                name.
        """
        attribute = AttributeRepository.get_by_id(attribute_id)
        normalized_name = name.strip()
        if AttributeRepository.name_exists(
            normalized_name, exclude_id=attribute.id
        ):
            raise AttributeNameAlreadyExistsError
        return AttributeRepository.update_name(attribute, name=normalized_name)

    @staticmethod
    def delete_attribute(attribute_id: int) -> None:
        """Delete an attribute and the ratings that use it.

        Args:
            attribute_id: Primary key of the attribute.

        Raises:
            Attribute.DoesNotExist: If the attribute does not exist.
        """
        attribute = AttributeRepository.get_by_id(attribute_id)
        AttributeRepository.delete(attribute)

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
        return PlayerAttributeRepository.create(
            player=player, attribute=attribute, value=value
        )

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
        return PlayerAttributeRepository.update_value(
            player_attribute, value=value
        )

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
        PlayerAttributeRepository.delete(player_attribute)
