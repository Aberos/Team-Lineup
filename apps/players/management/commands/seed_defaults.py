"""Command that registers the default roles and attributes."""

from django.core.management.base import BaseCommand

from apps.players.services import PlayerService


class Command(BaseCommand):
    """Create the default roles and attributes that are missing."""

    help = "Cria as funções e os atributos padrão que ainda não existem."

    def handle(self, *args: object, **options: object) -> None:
        """Run the seed and report what was created.

        Args:
            *args: Positional arguments of the command, unused.
            **options: Options of the command, unused.
        """
        result = PlayerService.seed_default_catalog()
        role_names = ", ".join(role.name for role in result.roles) or "nenhuma"
        attribute_names = (
            ", ".join(attribute.name for attribute in result.attributes)
            or "nenhum"
        )
        self.stdout.write(f"Funções criadas: {role_names}")
        self.stdout.write(f"Atributos criados: {attribute_names}")
