# Generated by Django 1.11.29 on 2023-02-02 14:43

import django.db.models.deletion
import sortedm2m.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0069_delete_blank_keywords"),
        ("jcom_profile", "0015_auto_20230103_1357"),
    ]

    operations = [
        migrations.CreateModel(
            name="Genealogy",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "children",
                    sortedm2m.fields.SortedManyToManyField(
                        help_text=None, related_name="ancestors", to="submission.Article"
                    ),
                ),
                (
                    "parent",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="genealogy",
                        to="submission.Article",
                        verbose_name="Introduction",
                    ),
                ),
            ],
        ),
    ]
