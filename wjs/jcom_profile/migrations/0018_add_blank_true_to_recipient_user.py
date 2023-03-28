# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2023-03-28 11:20
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jcom_profile', '0017_newsletter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipient',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Newsletter topics user'),
        ),
    ]