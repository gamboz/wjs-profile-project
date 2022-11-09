# Generated by Django 1.11.29 on 2022-11-09 18:07

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("journal", "0055_merge_20220926_1517"),
        ("jcom_profile", "0005_auto_20221018_0924"),
    ]

    operations = [
        migrations.CreateModel(
            name="PPFile",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file", models.FileField(upload_to="")),
                ("public", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="SIFiles",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ],
        ),
        migrations.RemoveField(
            model_name="specialissue",
            name="is_open_for_submission",
        ),
        migrations.AddField(
            model_name="specialissue",
            name="close_date",
            field=models.DateTimeField(
                blank=True, help_text="Authors cannot submit to this special issue after this date", null=True
            ),
        ),
        migrations.AddField(
            model_name="specialissue",
            name="description",
            field=models.TextField(default="desc", help_text="Description or abstract"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="specialissue",
            name="journal",
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to="journal.Journal"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="specialissue",
            name="open_date",
            field=models.DateTimeField(
                blank=True,
                default=django.utils.timezone.now,
                help_text="Authors can submit to this special issue only after this date",
            ),
        ),
        migrations.AddField(
            model_name="specialissue",
            name="short_name",
            field=models.SlugField(
                default="xxx", help_text="Short name or code (please only [a-zA-Z0-9_-]", max_length=21
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="specialissue",
            name="name",
            field=models.CharField(help_text="Name / title / long name", max_length=121),
        ),
        migrations.AddField(
            model_name="ppfile",
            name="special_issue",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="jcom_profile.SpecialIssue"),
        ),
    ]
