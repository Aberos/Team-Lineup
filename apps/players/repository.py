"""Repository for the players app."""

from datetime import date

from apps.players.models import Player, PlayerRole, Role


class RoleRepository:
    """Provide data access for roles."""

    @staticmethod
    def create(name: str) -> Role:
        """Persist a new role.

        Args:
            name: Display name of the role.

        Returns:
            The created role.
        """
        return Role.objects.create(name=name)

    @staticmethod
    def get_by_id(role_id: int) -> Role:
        """Return the role with the given identifier.

        Args:
            role_id: Primary key of the role.

        Returns:
            The matching role.

        Raises:
            Role.DoesNotExist: If no role has the given identifier.
        """
        return Role.objects.get(id=role_id)

    @staticmethod
    def list_all() -> list[Role]:
        """Return every role ordered by name."""
        return list(Role.objects.order_by("name"))

    @staticmethod
    def list_by_player(player_id: int) -> list[Role]:
        """Return the roles assigned to a player ordered by name.

        Args:
            player_id: Primary key of the player.

        Returns:
            The roles assigned to the player.
        """
        return list(
            Role.objects.filter(playerrole__player_id=player_id).order_by(
                "name"
            )
        )

    @staticmethod
    def update_name(role: Role, name: str) -> Role:
        """Change the name of a role.

        Args:
            role: Role to update.
            name: New display name.

        Returns:
            The updated role.
        """
        role.name = name
        role.save(update_fields=["name"])
        return role

    @staticmethod
    def delete(role: Role) -> None:
        """Remove a role.

        Args:
            role: Role to delete.
        """
        role.delete()


class PlayerRepository:
    """Provide data access for players."""

    @staticmethod
    def create(
        *,
        name: str,
        birthday: date,
        phone: str,
        email: str,
        number: int,
    ) -> Player:
        """Persist a new player.

        Args:
            name: Full name of the player.
            birthday: Birth date of the player.
            phone: Contact phone number.
            email: Unique contact email.
            number: Shirt number.

        Returns:
            The created player.
        """
        return Player.objects.create(
            name=name,
            birthday=birthday,
            phone=phone,
            email=email,
            number=number,
        )

    @staticmethod
    def get_by_id(player_id: int) -> Player:
        """Return the player with the given identifier.

        Args:
            player_id: Primary key of the player.

        Returns:
            The matching player.

        Raises:
            Player.DoesNotExist: If no player has the given identifier.
        """
        return Player.objects.get(id=player_id)

    @staticmethod
    def list_all() -> list[Player]:
        """Return every player ordered by name."""
        return list(Player.objects.order_by("name"))

    @staticmethod
    def email_exists(email: str, exclude_id: int | None = None) -> bool:
        """Check whether a player already uses the given email.

        Args:
            email: Email to look for.
            exclude_id: Primary key of a player to ignore in the search.

        Returns:
            True when another player uses the email.
        """
        queryset = Player.objects.filter(email=email)
        if exclude_id is not None:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.exists()

    @staticmethod
    def update(
        player: Player,
        *,
        name: str,
        birthday: date,
        phone: str,
        email: str,
        number: int,
    ) -> Player:
        """Replace every editable field of a player.

        Args:
            player: Player to update.
            name: Full name of the player.
            birthday: Birth date of the player.
            phone: Contact phone number.
            email: Unique contact email.
            number: Shirt number.

        Returns:
            The updated player.
        """
        player.name = name
        player.birthday = birthday
        player.phone = phone
        player.email = email
        player.number = number
        player.save(
            update_fields=["name", "birthday", "phone", "email", "number"]
        )
        return player

    @staticmethod
    def delete(player: Player) -> None:
        """Remove a player.

        Args:
            player: Player to delete.
        """
        player.delete()


class PlayerRoleRepository:
    """Provide data access for the player-role relationship."""

    @staticmethod
    def create(player: Player, role: Role) -> PlayerRole:
        """Assign a role to a player.

        Args:
            player: Player that receives the role.
            role: Role to assign.

        Returns:
            The created relationship.
        """
        return PlayerRole.objects.create(player=player, role=role)

    @staticmethod
    def exists(player_id: int, role_id: int) -> bool:
        """Check whether the player already has the role.

        Args:
            player_id: Primary key of the player.
            role_id: Primary key of the role.

        Returns:
            True when the relationship exists.
        """
        return PlayerRole.objects.filter(
            player_id=player_id, role_id=role_id
        ).exists()

    @staticmethod
    def get(player_id: int, role_id: int) -> PlayerRole:
        """Return the relationship between a player and a role.

        Args:
            player_id: Primary key of the player.
            role_id: Primary key of the role.

        Returns:
            The matching relationship.

        Raises:
            PlayerRole.DoesNotExist: If the player does not have the role.
        """
        return PlayerRole.objects.get(player_id=player_id, role_id=role_id)

    @staticmethod
    def delete(player_role: PlayerRole) -> None:
        """Remove a role from a player.

        Args:
            player_role: Relationship to delete.
        """
        player_role.delete()
