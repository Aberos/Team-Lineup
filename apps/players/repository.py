"""Repository for the players app."""

from datetime import date

from apps.players.models import (
    Attribute,
    Player,
    PlayerAttribute,
    PlayerRole,
    Role,
)


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
    def name_exists(name: str) -> bool:
        """Check whether a role already uses the given name.

        Args:
            name: Name to look for, compared without case.

        Returns:
            True when a role uses the name.
        """
        return Role.objects.filter(name__iexact=name).exists()

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


class AttributeRepository:
    """Provide data access for the attribute catalog."""

    @staticmethod
    def create(name: str) -> Attribute:
        """Persist a new attribute.

        Args:
            name: Unique display name of the attribute.

        Returns:
            The created attribute.
        """
        return Attribute.objects.create(name=name)

    @staticmethod
    def get_by_id(attribute_id: int) -> Attribute:
        """Return the attribute with the given identifier.

        Args:
            attribute_id: Primary key of the attribute.

        Returns:
            The matching attribute.

        Raises:
            Attribute.DoesNotExist: If no attribute has the identifier.
        """
        return Attribute.objects.get(id=attribute_id)

    @staticmethod
    def list_all() -> list[Attribute]:
        """Return every attribute ordered by name."""
        return list(Attribute.objects.order_by("name"))

    @staticmethod
    def name_exists(name: str, exclude_id: int | None = None) -> bool:
        """Check whether an attribute already uses the given name.

        Args:
            name: Name to look for, compared without case.
            exclude_id: Primary key of an attribute to ignore.

        Returns:
            True when another attribute uses the name.
        """
        queryset = Attribute.objects.filter(name__iexact=name)
        if exclude_id is not None:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.exists()

    @staticmethod
    def update_name(attribute: Attribute, name: str) -> Attribute:
        """Change the name of an attribute.

        Args:
            attribute: Attribute to update.
            name: New display name.

        Returns:
            The updated attribute.
        """
        attribute.name = name
        attribute.save(update_fields=["name"])
        return attribute

    @staticmethod
    def delete(attribute: Attribute) -> None:
        """Remove an attribute and every rating that uses it.

        Args:
            attribute: Attribute to delete.
        """
        attribute.delete()


class PlayerAttributeRepository:
    """Provide data access for the ratings of players."""

    @staticmethod
    def create(
        *, player: Player, attribute: Attribute, value: int
    ) -> PlayerAttribute:
        """Persist the rating of a player in an attribute.

        Args:
            player: Rated player.
            attribute: Rated attribute.
            value: Rating between the allowed bounds.

        Returns:
            The created rating with its attribute loaded.
        """
        return PlayerAttribute.objects.create(
            player=player, attribute=attribute, value=value
        )

    @staticmethod
    def exists(player_id: int, attribute_id: int) -> bool:
        """Check whether the player already has a rating for the attribute.

        Args:
            player_id: Primary key of the player.
            attribute_id: Primary key of the attribute.

        Returns:
            True when the rating exists.
        """
        return PlayerAttribute.objects.filter(
            player_id=player_id, attribute_id=attribute_id
        ).exists()

    @staticmethod
    def get(player_id: int, attribute_id: int) -> PlayerAttribute:
        """Return the rating of a player in an attribute.

        Args:
            player_id: Primary key of the player.
            attribute_id: Primary key of the attribute.

        Returns:
            The matching rating with its attribute loaded.

        Raises:
            PlayerAttribute.DoesNotExist: If the player has no rating for
                the attribute.
        """
        return PlayerAttribute.objects.select_related("attribute").get(
            player_id=player_id, attribute_id=attribute_id
        )

    @staticmethod
    def list_by_player(player_id: int) -> list[PlayerAttribute]:
        """Return the ratings of a player ordered by attribute name.

        Args:
            player_id: Primary key of the player.

        Returns:
            The ratings with their attributes loaded.
        """
        return list(
            PlayerAttribute.objects.select_related("attribute")
            .filter(player_id=player_id)
            .order_by("attribute__name")
        )

    @staticmethod
    def update_value(
        player_attribute: PlayerAttribute, value: int
    ) -> PlayerAttribute:
        """Change the value of a rating.

        Args:
            player_attribute: Rating to update.
            value: New rating between the allowed bounds.

        Returns:
            The updated rating.
        """
        player_attribute.value = value
        player_attribute.save(update_fields=["value"])
        return player_attribute

    @staticmethod
    def delete(player_attribute: PlayerAttribute) -> None:
        """Remove a rating.

        Args:
            player_attribute: Rating to delete.
        """
        player_attribute.delete()
