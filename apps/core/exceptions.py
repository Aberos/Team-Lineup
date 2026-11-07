"""Domain exceptions for the core app."""


class InvalidCredentialsError(Exception):
    """Raise when the provided credentials do not match a valid user."""
