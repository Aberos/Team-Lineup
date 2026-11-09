"""Repository for the players app."""

from datetime import date

from django.contrib.auth.models import User
from django.core.files.uploadedfile import UploadedFile
from django.db.models import F, OrderBy, Prefetch

from apps.players.models import (
    Attribute,
    OverallFormula,
    Player,
    PlayerAttribute,
    PlayerOrdering,
    PlayerRole,
    Role,
)

_PLAYER_ORDERINGS: dict[str, tuple[OrderBy | str, ...]] = {
    PlayerOrdering.NAME: ("name", "id"),
    PlayerOrdering.NAME_DESC: ("-name", "-id"),
    PlayerOrdering.OVERALL: (F("overall").asc(nulls_last=True), "name"),
    PlayerOrdering.OVERALL_DESC: (F("overall").desc(nulls_last=True), "name"),
}


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
    def search_page(
        *,
        search: str,
        role_id: int | None,
        ordering: str,
        offset: int,
        limit: int,
    ) -> tuple[list[Player], int]:
        """Return one page of players with their card data preloaded.

        Args:
            search: Text that the player name must contain, ignoring case.
            role_id: Primary key of a role the player must have.
            ordering: Value of ``PlayerOrdering``.
            offset: Number of players to skip.
            limit: Maximum number of players to return.

        Returns:
            The players of the page and the total of matching players.
        """
        queryset = Player.objects.all()
        if search:
            queryset = queryset.filter(name__icontains=search)
        if role_id is not None:
            queryset = queryset.filter(playerrole__role_id=role_id)
        total = queryset.count()
        players = list(
            queryset.order_by(*_PLAYER_ORDERINGS[ordering]).prefetch_related(
                Prefetch(
                    "playerrole_set",
                    queryset=PlayerRole.objects.select_related(
                        "role"
                    ).order_by("-is_primary", "role__name"),
                ),
                Prefetch(
                    "playerattribute_set",
                    queryset=PlayerAttribute.objects.filter(
                        attribute__card_order__isnull=False
                    ),
                ),
            )[offset : offset + limit]
        )
        return players, total

    @staticmethod
    def preloaded_roles(player: Player) -> list[PlayerRole]:
        """Return the roles loaded by ``search_page``, primary first.

        Args:
            player: Player returned by ``search_page``.

        Returns:
            The relationships with their roles.
        """
        return list(player.playerrole_set.all())

    @staticmethod
    def preloaded_card_ratings(player: Player) -> list[PlayerAttribute]:
        """Return the card ratings loaded by ``search_page``.

        Args:
            player: Player returned by ``search_page``.

        Returns:
            The ratings of attributes shown on cards.
        """
        return list(player.playerattribute_set.all())

    @staticmethod
    def list_ids() -> list[int]:
        """Return the primary key of every player."""
        return list(Player.objects.values_list("id", flat=True))

    @staticmethod
    def list_by_name(limit: int | None = None) -> list[Player]:
        """Return players ordered by name.

        Args:
            limit: Maximum number of players, or None for all of them.

        Returns:
            The players.
        """
        queryset = Player.objects.order_by("name", "id")
        return list(queryset if limit is None else queryset[:limit])

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
    def update_overall(player_id: int, overall: int | None) -> None:
        """Store the overall rating of a player.

        Args:
            player_id: Primary key of the player.
            overall: New overall rating, or None when it cannot be computed.
        """
        Player.objects.filter(id=player_id).update(overall=overall)

    @staticmethod
    def replace_photo(player: Player, photo: UploadedFile) -> Player:
        """Store a new photo for the player and delete the previous file.

        Args:
            player: Player that receives the photo.
            photo: Uploaded image file.

        Returns:
            The updated player.
        """
        previous_name = player.photo.name
        player.photo.save(photo.name or "photo", photo, save=False)
        player.save(update_fields=["photo"])
        if previous_name and previous_name != player.photo.name:
            player.photo.storage.delete(previous_name)
        return player

    @staticmethod
    def remove_photo(player: Player) -> Player:
        """Delete the photo file of the player.

        Args:
            player: Player whose photo is removed.

        Returns:
            The updated player.
        """
        if player.photo:
            player.photo.delete(save=False)
        player.photo.name = ""
        player.save(update_fields=["photo"])
        return player

    @staticmethod
    def delete(player: Player) -> None:
        """Remove a player and its photo file.

        Args:
            player: Player to delete.
        """
        if player.photo:
            player.photo.delete(save=False)
        player.delete()


class PlayerRoleRepository:
    """Provide data access for the player-role relationship."""

    @staticmethod
    def create(player: Player, role: Role, *, is_primary: bool) -> PlayerRole:
        """Assign a role to a player.

        Args:
            player: Player that receives the role.
            role: Role to assign.
            is_primary: Whether the role becomes the primary one.

        Returns:
            The created relationship.
        """
        return PlayerRole.objects.create(
            player=player, role=role, is_primary=is_primary
        )

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
    def has_any(player_id: int) -> bool:
        """Check whether the player has at least one role.

        Args:
            player_id: Primary key of the player.

        Returns:
            True when the player has a role.
        """
        return PlayerRole.objects.filter(player_id=player_id).exists()

    @staticmethod
    def get(player_id: int, role_id: int) -> PlayerRole:
        """Return the relationship between a player and a role.

        Args:
            player_id: Primary key of the player.
            role_id: Primary key of the role.

        Returns:
            The matching relationship with its role loaded.

        Raises:
            PlayerRole.DoesNotExist: If the player does not have the role.
        """
        return PlayerRole.objects.select_related("role").get(
            player_id=player_id, role_id=role_id
        )

    @staticmethod
    def list_by_player(player_id: int) -> list[PlayerRole]:
        """Return the roles of a player, primary first, then by name.

        Args:
            player_id: Primary key of the player.

        Returns:
            The relationships with their roles loaded.
        """
        return list(
            PlayerRole.objects.select_related("role")
            .filter(player_id=player_id)
            .order_by("-is_primary", "role__name")
        )

    @staticmethod
    def get_primary(player_id: int) -> PlayerRole | None:
        """Return the primary role of a player.

        Args:
            player_id: Primary key of the player.

        Returns:
            The primary relationship, or None when there is none.
        """
        return PlayerRole.objects.filter(
            player_id=player_id, is_primary=True
        ).first()

    @staticmethod
    def players_with_primary(role_id: int) -> list[int]:
        """Return the players that have the role as their primary one.

        Args:
            role_id: Primary key of the role.

        Returns:
            Primary keys of the players.
        """
        return list(
            PlayerRole.objects.filter(
                role_id=role_id, is_primary=True
            ).values_list("player_id", flat=True)
        )

    @staticmethod
    def players_with_role(role_id: int) -> list[int]:
        """Return the players that have the role.

        Args:
            role_id: Primary key of the role.

        Returns:
            Primary keys of the players.
        """
        return list(
            PlayerRole.objects.filter(role_id=role_id).values_list(
                "player_id", flat=True
            )
        )

    @staticmethod
    def first_assigned(player_id: int) -> PlayerRole | None:
        """Return the oldest role assignment of a player.

        Args:
            player_id: Primary key of the player.

        Returns:
            The oldest relationship, or None when the player has no role.
        """
        return (
            PlayerRole.objects.filter(player_id=player_id)
            .order_by("id")
            .first()
        )

    @staticmethod
    def set_primary(
        player_role: PlayerRole, *, is_primary: bool
    ) -> PlayerRole:
        """Mark or unmark a relationship as the primary role.

        Args:
            player_role: Relationship to update.
            is_primary: New value of the flag.

        Returns:
            The updated relationship.
        """
        player_role.is_primary = is_primary
        player_role.save(update_fields=["is_primary"])
        return player_role

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
    def create(
        *, name: str, abbreviation: str, card_order: int | None
    ) -> Attribute:
        """Persist a new attribute.

        Args:
            name: Unique display name of the attribute.
            abbreviation: Short label shown on cards.
            card_order: Slot on the card, or None when not shown.

        Returns:
            The created attribute.
        """
        return Attribute.objects.create(
            name=name, abbreviation=abbreviation, card_order=card_order
        )

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
    def list_card_attributes() -> list[Attribute]:
        """Return the attributes shown on cards in slot order."""
        return list(
            Attribute.objects.filter(card_order__isnull=False).order_by(
                "card_order"
            )
        )

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
    def abbreviation_exists(
        abbreviation: str, exclude_id: int | None = None
    ) -> bool:
        """Check whether an attribute already uses the given abbreviation.

        Args:
            abbreviation: Abbreviation to look for, compared without case.
            exclude_id: Primary key of an attribute to ignore.

        Returns:
            True when another attribute uses the abbreviation.
        """
        queryset = Attribute.objects.filter(abbreviation__iexact=abbreviation)
        if exclude_id is not None:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.exists()

    @staticmethod
    def card_slot_taken(
        card_order: int, exclude_id: int | None = None
    ) -> bool:
        """Check whether another attribute occupies the card slot.

        Args:
            card_order: Slot on the card.
            exclude_id: Primary key of an attribute to ignore.

        Returns:
            True when the slot is taken.
        """
        queryset = Attribute.objects.filter(card_order=card_order)
        if exclude_id is not None:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.exists()

    @staticmethod
    def update(
        attribute: Attribute,
        *,
        name: str,
        abbreviation: str,
        card_order: int | None,
    ) -> Attribute:
        """Replace every editable field of an attribute.

        Args:
            attribute: Attribute to update.
            name: New display name.
            abbreviation: New short label shown on cards.
            card_order: New slot on the card, or None when not shown.

        Returns:
            The updated attribute.
        """
        attribute.name = name
        attribute.abbreviation = abbreviation
        attribute.card_order = card_order
        attribute.save(update_fields=["name", "abbreviation", "card_order"])
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
    def card_ratings_by_abbreviation(player_id: int) -> dict[str, int]:
        """Return the card ratings of a player keyed by abbreviation.

        Args:
            player_id: Primary key of the player.

        Returns:
            Rating values keyed by the attribute abbreviation.
        """
        return dict(
            PlayerAttribute.objects.filter(
                player_id=player_id, attribute__card_order__isnull=False
            ).values_list("attribute__abbreviation", "value")
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


class OverallFormulaRepository:
    """Provide data access for overall formula versions."""

    @staticmethod
    def create(
        *, script: str, description: str, created_by: User | None
    ) -> OverallFormula:
        """Persist a new, inactive formula version.

        Args:
            script: Lua source of the formula.
            description: Short note about the version.
            created_by: Author of the version.

        Returns:
            The created formula.
        """
        return OverallFormula.objects.create(
            script=script, description=description, created_by=created_by
        )

    @staticmethod
    def get_by_id(formula_id: int) -> OverallFormula:
        """Return the formula with the given identifier.

        Args:
            formula_id: Primary key of the formula.

        Returns:
            The matching formula with its author loaded.

        Raises:
            OverallFormula.DoesNotExist: If no formula has the identifier.
        """
        return OverallFormula.objects.select_related("created_by").get(
            id=formula_id
        )

    @staticmethod
    def list_all() -> list[OverallFormula]:
        """Return every formula version, newest first."""
        return list(
            OverallFormula.objects.select_related("created_by").order_by(
                "-created_at", "-id"
            )
        )

    @staticmethod
    def get_active() -> OverallFormula | None:
        """Return the formula in use, or None when the average is used."""
        return (
            OverallFormula.objects.select_related("created_by")
            .filter(is_active=True)
            .first()
        )

    @staticmethod
    def deactivate_all() -> None:
        """Mark every formula as inactive."""
        OverallFormula.objects.filter(is_active=True).update(is_active=False)

    @staticmethod
    def activate(formula: OverallFormula) -> OverallFormula:
        """Make the formula the only active one.

        Args:
            formula: Formula to activate.

        Returns:
            The activated formula.
        """
        OverallFormulaRepository.deactivate_all()
        formula.is_active = True
        formula.save(update_fields=["is_active"])
        return formula

    @staticmethod
    def delete(formula: OverallFormula) -> None:
        """Remove a formula version.

        Args:
            formula: Formula to delete.
        """
        formula.delete()
