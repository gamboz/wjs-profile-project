# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-04-26 12:45
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0069_auto_20220426_1403'),
    ]

    operations = [
        migrations.CreateModel(
            name='JCOMProfile',
            fields=[
                ('account_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('profession', models.IntegerField(choices=[(0, 'A researcher in S&T studies, science communication or neighbouring field'), (1, 'A practitioner in S&T (e.g. journalist, museum staff, writer, ...)'), (2, 'An active scientist'), (3, 'Other')])),
            ],
            options={
                'abstract': False,
            },
            bases=('core.account',),
        ),
    ]
