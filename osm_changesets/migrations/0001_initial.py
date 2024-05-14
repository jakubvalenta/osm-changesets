# Generated by Django 5.0.6 on 2024-05-10 21:22

import django.db.models.deletion
import osm_changesets.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("uid", models.IntegerField(primary_key=True, serialize=False)),
                ("user_name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Changeset",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("comment", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("max_lat", models.FloatField()),
                ("max_lon", models.FloatField()),
                ("min_lat", models.FloatField()),
                ("min_lon", models.FloatField()),
                (
                    "svg",
                    models.FileField(
                        upload_to=osm_changesets.models.changeset_upload_to
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="changesets",
                        to="osm_changesets.user",
                    ),
                ),
            ],
        ),
    ]