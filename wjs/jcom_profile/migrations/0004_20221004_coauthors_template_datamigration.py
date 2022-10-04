# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-10-04 08:40
from __future__ import unicode_literals

from django.db import migrations
from django.utils.translation import ugettext_lazy as _


def add_coauthors_submission_email_subject_and_template(apps, schema_editor):
    Setting = apps.get_model('core', 'Setting')
    SettingValue = apps.get_model('core', 'SettingValue')
    Group = apps.get_model('core', 'SettingGroup')

    email_settings_group = Group.objects.get(name='email')
    email_subject_settings_group = Group.objects.get(name='email_subject')

    coauthor_submission_email_template = Setting.objects.create(
        name="submission_coauthors_acknowledgment",
        group=email_settings_group,
        types="rich-text",
        pretty_name=_("Submission Coauthors Acknowledgement"),
        description=_("Email sent to coauthors when they have submitted an article."),
        is_translatable=True
    )

    coauthor_submission_email_subject = Setting.objects.create(
        name="subject_submission_coauthors_acknowledgement",
        group=email_subject_settings_group,
        types="text",
        pretty_name=_("Submission Subject Coauthors Acknowledgement"),
        description=_("Subject for Email sent to coauthors when they have submitted an article."),
        is_translatable=True
    )

    SettingValue.objects.create(
        journal=None,
        setting=coauthor_submission_email_template,
        value="Dear {{ author.full_name}}, <br><br>Thank you for submitting \"{{ article }}\" to {{ article.journal }} as coauthor.<br><br> Your work will now be reviewed by an editor and we will be in touch as the peer-review process progresses.<br><br>Regards,<br>",
        value_en="Dear {{ author.full_name}}, <br><br>Thank you for submitting \"{{ article }}\" to {{ article.journal }} as coauthor.<br><br> Your work will now be reviewed by an editor and we will be in touch as the peer-review process progresses.<br><br>Regards,<br>"
    )

    SettingValue.objects.create(
        journal=None,
        setting=coauthor_submission_email_subject,
        value="Coauthor - Article Submission",
        value_en="Coauthor - Article Submission"
    )


class Migration(migrations.Migration):
    dependencies = [
        ('jcom_profile', '0003_jcomprofile_invitation_token'),
    ]

    operations = [
        migrations.RunPython(add_coauthors_submission_email_subject_and_template)
    ]
