"""Domain exceptions for the players app."""


class PlayerEmailAlreadyExistsError(Exception):
    """Raise when another player already uses the given email."""


class PlayerRoleAlreadyAssignedError(Exception):
    """Raise when the role is already assigned to the player."""


class AttributeNameAlreadyExistsError(Exception):
    """Raise when another attribute already uses the given name."""


class PlayerAttributeAlreadyExistsError(Exception):
    """Raise when the player already has a rating for the attribute."""
