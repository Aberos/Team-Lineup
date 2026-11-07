"""Domain exceptions for the events app."""


class PlayerNotFoundError(Exception):
    """Raise when a referenced player does not exist."""


class ParticipantAlreadyExistsError(Exception):
    """Raise when the player already participates in the event."""


class TeamNameAlreadyExistsError(Exception):
    """Raise when the event already has a team with the given name."""


class PlayerNotParticipantError(Exception):
    """Raise when the player does not participate in the event."""


class PlayerAlreadyInTeamError(Exception):
    """Raise when the player already belongs to a team of the event."""


class TeamNotInEventError(Exception):
    """Raise when a referenced team does not belong to the event."""
