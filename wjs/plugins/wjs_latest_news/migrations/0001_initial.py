# Generated by Django 1.11.29 on 2023-02-28 14:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("journal", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="PluginConfig",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(help_text="Section title", max_length=500)),
                (
                    "count",
                    models.PositiveSmallIntegerField(default=10, help_text="Number of items shown in the home page"),
                ),
                ("journal", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="journal.Journal", related_name='wjs_latest_news_plugin_config')),
            ],
        ),
    ]
