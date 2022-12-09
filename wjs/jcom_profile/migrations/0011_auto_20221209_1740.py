# Generated by Django 1.11.29 on 2022-12-09 16:40

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jcom_profile", "0010_auto_20221202_1451"),
    ]

    operations = [
        migrations.AlterField(
            model_name="specialissue",
            name="documents",
            field=models.ManyToManyField(blank=True, null=True, to="core.File"),
        ),
        migrations.AlterField(
            model_name="specialissue",
            name="invitees",
            field=models.ManyToManyField(blank=True, null=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
