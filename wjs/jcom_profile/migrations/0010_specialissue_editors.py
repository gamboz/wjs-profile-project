# Generated by Django 1.11.29 on 2022-12-05 11:20

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("jcom_profile", "0009_specialissue_allowed_sections"),
    ]

    operations = [
        migrations.AddField(
            model_name="specialissue",
            name="editors",
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
