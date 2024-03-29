# Generated by Django 1.11.29 on 2022-11-18 12:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0069_delete_blank_keywords"),
        ("journal", "0055_issue_isbn"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("jcom_profile", "0006_auto_20221116_1538"),
    ]

    operations = [
        migrations.CreateModel(
            name="EditorAssignmentParameters",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("workload", models.PositiveSmallIntegerField(default=0)),
                ("brake_on", models.PositiveSmallIntegerField(default=0)),
                (
                    "editor",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
                ("journal", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="journal.Journal")),
            ],
        ),
        migrations.CreateModel(
            name="EditorKeyword",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("weight", models.PositiveIntegerField(default=0)),
                (
                    "editor_parameters",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="jcom_profile.EditorAssignmentParameters"
                    ),
                ),
                ("keyword", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="submission.Keyword")),
            ],
        ),
        migrations.AddField(
            model_name="editorassignmentparameters",
            name="keywords",
            field=models.ManyToManyField(through="jcom_profile.EditorKeyword", to="submission.Keyword"),
        ),
    ]
