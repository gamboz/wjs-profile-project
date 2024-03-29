# Generated by Django 1.11.29 on 2022-12-22 10:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("journal", "0055_issue_isbn"),
        ("submission", "0069_delete_blank_keywords"),
        ("jcom_profile", "0013_merge_20221222_0935"),
    ]

    operations = [
        migrations.CreateModel(
            name="Recipient",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("news", models.BooleanField(default=False, verbose_name="Generic news topic")),
                (
                    "journal",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="journal.Journal",
                        verbose_name="Newsletter topics' journal",
                    ),
                ),
                (
                    "topics",
                    models.ManyToManyField(blank=True, to="submission.Keyword", verbose_name="Newsletters topics"),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Newsletter topics user",
                    ),
                ),
            ],
            options={
                "verbose_name": "recipient",
                "verbose_name_plural": "recipients",
            },
        ),
    ]
