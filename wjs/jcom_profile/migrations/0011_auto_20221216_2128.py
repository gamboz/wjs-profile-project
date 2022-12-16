# Generated by Django 1.11.29 on 2022-12-16 20:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("jcom_profile", "0010_specialissue_editors"),
    ]

    operations = [
        migrations.AddField(
            model_name="specialissue",
            name="invitees",
            field=models.ManyToManyField(related_name="special_issue_invited", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name="articlewrapper",
            name="special_issue",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="articles",
                to="jcom_profile.SpecialIssue",
            ),
        ),
    ]
