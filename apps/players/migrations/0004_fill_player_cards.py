"""Fill the card data introduced by the previous migration."""

from django.apps.registry import Apps
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor

ABBREVIATION_LENGTH = 3
DEFAULT_CARD_ATTRIBUTES: dict[str, tuple[str, int]] = {
    "velocidade": ("VEL", 1),
    "finalização": ("FIN", 2),
    "passe": ("PAS", 3),
    "drible": ("DRI", 4),
    "defesa": ("DEF", 5),
    "físico": ("FÍS", 6),
}
ROUNDING_OFFSET = 0.5


def fill_attributes(
    apps: Apps, schema_editor: BaseDatabaseSchemaEditor
) -> None:
    """Give every attribute an abbreviation and place the defaults on cards.

    Args:
        apps: Historical app registry.
        schema_editor: Editor of the current database connection.
    """
    attribute_model = apps.get_model("players", "Attribute")
    for attribute in attribute_model.objects.all():
        default = DEFAULT_CARD_ATTRIBUTES.get(attribute.name.lower())
        if default is None:
            attribute.abbreviation = attribute.name[
                :ABBREVIATION_LENGTH
            ].upper()
        else:
            attribute.abbreviation, attribute.card_order = default
        attribute.save(update_fields=["abbreviation", "card_order"])


def mark_primary_roles(
    apps: Apps, schema_editor: BaseDatabaseSchemaEditor
) -> None:
    """Mark the oldest role of every player as the primary one.

    Args:
        apps: Historical app registry.
        schema_editor: Editor of the current database connection.
    """
    player_role_model = apps.get_model("players", "PlayerRole")
    seen_players: set[int] = set()
    for player_role in player_role_model.objects.order_by("player_id", "id"):
        if player_role.player_id in seen_players:
            continue
        seen_players.add(player_role.player_id)
        player_role.is_primary = True
        player_role.save(update_fields=["is_primary"])


def compute_overalls(
    apps: Apps, schema_editor: BaseDatabaseSchemaEditor
) -> None:
    """Store the average of the card ratings as the overall of each player.

    Args:
        apps: Historical app registry.
        schema_editor: Editor of the current database connection.
    """
    player_model = apps.get_model("players", "Player")
    rating_model = apps.get_model("players", "PlayerAttribute")
    for player in player_model.objects.all():
        values = list(
            rating_model.objects.filter(
                player_id=player.id, attribute__card_order__isnull=False
            ).values_list("value", flat=True)
        )
        player.overall = (
            int(sum(values) / len(values) + ROUNDING_OFFSET)
            if values
            else None
        )
        player.save(update_fields=["overall"])


class Migration(migrations.Migration):
    """Fill abbreviations, card slots, primary roles and overalls."""

    dependencies = [
        ("players", "0003_player_cards"),
    ]

    operations = [
        migrations.RunPython(fill_attributes, migrations.RunPython.noop),
        migrations.RunPython(mark_primary_roles, migrations.RunPython.noop),
        migrations.RunPython(compute_overalls, migrations.RunPython.noop),
    ]
