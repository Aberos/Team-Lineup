import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("players", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Event",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("date", models.DateField()),
                ("location", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="EventTeam",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("team_name", models.CharField(max_length=100)),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="events.event",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="EventMatch",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("score_team_home", models.IntegerField()),
                ("score_team_away", models.IntegerField()),
                (
                    "status",
                    models.IntegerField(
                        choices=[
                            (0, "Scheduled"),
                            (1, "Ongoing"),
                            (2, "Completed"),
                        ],
                        default=0,
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="events.event",
                    ),
                ),
                (
                    "team_away",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="team2_matches",
                        to="events.eventteam",
                    ),
                ),
                (
                    "team_home",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="team1_matches",
                        to="events.eventteam",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TeamMembership",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "participant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="players.player",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="events.eventteam",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="EventParticipation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("score", models.IntegerField()),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="events.event",
                    ),
                ),
                (
                    "player",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="players.player",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("player", "event"),
                        name="unique_event_participation",
                    )
                ],
            },
        ),
        migrations.AddConstraint(
            model_name="eventteam",
            constraint=models.UniqueConstraint(
                fields=("event", "team_name"), name="unique_event_team_name"
            ),
        ),
        migrations.AddConstraint(
            model_name="eventmatch",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("team_home", models.F("team_away")), _negated=True
                ),
                name="match_teams_must_differ",
            ),
        ),
        migrations.AddConstraint(
            model_name="teammembership",
            constraint=models.UniqueConstraint(
                fields=("team", "participant"), name="unique_team_membership"
            ),
        ),
    ]
