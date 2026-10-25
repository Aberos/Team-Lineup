"""Services for the players app."""

from apps.players.models import Role


class PlayerService:
    """Service class for player-related operations."""

    @staticmethod
    def create_role(name: str) -> None:
        """Create a new role with the given name."""
        role = Role(name=name)
        role.save()

    @staticmethod
    def list_roles() -> list[dict]:
        """List all roles."""
        roles = Role.objects.values("id", "name")
        return [{"id": role["id"], "name": role["name"]} for role in roles]

    @staticmethod
    def get_role_by_id(role_id: int) -> Role:
        """Retrieve a specific role by ID."""
        return Role.objects.get(id=role_id)

    @staticmethod
    def delete_role(role_id: int) -> None:
        """Delete a specific role by ID."""
        role = Role.objects.get(id=role_id)
        role.delete()

    @staticmethod
    def update_role(role_id: int, name: str) -> Role:
        """Update a specific role by ID."""
        role = Role.objects.get(id=role_id)
        if not role:
            raise Role.DoesNotExist("Role not found.")

        role.name = name
        role.save(update_fields=["name"])
        return role
