# Generated by Django 1.11.29 on 2023-02-13 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jcom_profile", "0016_genealogy"),
    ]

    operations = [
        migrations.CreateModel(
            name="Newsletter",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "last_sent",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Last time newsletter emails have been sent to users"
                    ),
                ),
            ],
        ),
    ]
