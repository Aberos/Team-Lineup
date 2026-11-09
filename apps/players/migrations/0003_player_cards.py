from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("players", "0002_player_attributes"),
    ]

    operations = [
        migrations.AddField(
            model_name="attribute",
            name="abbreviation",
            field=models.CharField(default="", max_length=4),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="attribute",
            name="card_order",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, unique=True
            ),
        ),
        migrations.AddField(
            model_name="player",
            name="overall",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="player",
            name="photo",
            field=models.ImageField(
                blank=True, default="", upload_to="players/"
            ),
        ),
        migrations.AddField(
            model_name="playerrole",
            name="is_primary",
            field=models.BooleanField(default=False),
        ),
        migrations.AddConstraint(
            model_name="attribute",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("card_order__isnull", True),
                    models.Q(("card_order__gte", 1), ("card_order__lte", 6)),
                    _connector="OR",
                ),
                name="attribute_card_order_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="player",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("overall__isnull", True),
                    models.Q(("overall__gte", 0), ("overall__lte", 100)),
                    _connector="OR",
                ),
                name="player_overall_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="playerrole",
            constraint=models.UniqueConstraint(
                condition=models.Q(("is_primary", True)),
                fields=("player",),
                name="unique_primary_role_per_player",
            ),
        ),
    ]
