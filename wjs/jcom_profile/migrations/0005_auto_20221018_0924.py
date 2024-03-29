# Generated by Django 1.11.29 on 2022-10-18 07:24

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("jcom_profile", "0004_specialissue_squashed_0008_auto_20221013_1539"),
    ]

    operations = [
        migrations.RenameField(
            model_name="correspondence",
            old_name="userCod",
            new_name="user_cod",
        ),
        migrations.AlterUniqueTogether(
            name="correspondence",
            unique_together={("account", "user_cod", "source")},
        ),
    ]
