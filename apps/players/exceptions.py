"""Domain exceptions for the players app."""


class PlayerEmailAlreadyExistsError(Exception):
    """Raise when another player already uses the given email."""


class PlayerRoleAlreadyAssignedError(Exception):
    """Raise when the role is already assigned to the player."""


class AttributeNameAlreadyExistsError(Exception):
    """Raise when another attribute already uses the given name."""


class PlayerAttributeAlreadyExistsError(Exception):
    """Raise when the player already has a rating for the attribute."""


class AttributeAbbreviationAlreadyExistsError(Exception):
    """Raise when another attribute already uses the given abbreviation."""


class CardSlotTakenError(Exception):
    """Raise when another attribute already occupies the card slot."""


class FormulaError(Exception):
    """Raise when an overall formula cannot be compiled or evaluated."""

    def __init__(self, message: str) -> None:
        """Store a readable description of the problem.

        Args:
            message: Description shown to the administrator.
        """
        super().__init__(message)
        self.message = message


class FormulaActivationError(Exception):
    """Raise when a formula fails for some players and cannot be activated."""

    def __init__(self, failures: list[tuple[int, str, str]]) -> None:
        """Store the players for which the formula failed.

        Args:
            failures: Player id, player name and error message per failure.
        """
        super().__init__("The formula failed for some players.")
        self.failures = failures


class ActiveFormulaDeletionError(Exception):
    """Raise when trying to delete the formula currently in use."""
