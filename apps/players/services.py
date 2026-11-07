"""Services for the players app."""

from datetime import date

from apps.players.exceptions import (
    PlayerEmailAlreadyExistsError,
    PlayerRoleAlreadyAssignedError,
)
from apps.players.models import Player, Role
from apps.players.repository import (
    PlayerRepository,
    PlayerRoleRepository,
    RoleRepository,
)


class PlayerService:
    """Business rules for players and roles."""

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
