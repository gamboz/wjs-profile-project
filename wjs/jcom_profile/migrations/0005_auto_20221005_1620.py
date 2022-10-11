"""New Janeway setting to parametrize title of additional files upload form."""
# Generated by Django 1.11.29 on 2022-10-05 14:20
from django.db import migrations
from django.utils.translation import ugettext_lazy as _


def add_submission_figures_data_title(apps, schema_editor):
    """Add a new setting."""
    Setting = apps.get_model('core', 'Setting')
    SettingValue = apps.get_model('core', 'SettingValue')
    Group = apps.get_model('core', 'SettingGroup')

    # TODO: other choices: general | app:wjs
    styling_settings_group = Group.objects.get(name='styling')

    submission_figures_data_title = Setting.objects.create(
        name="submission_figures_data_title",
        group=styling_settings_group,
        types="rich-text",
        pretty_name=_("Files Submission - Title of Figures and Data Files Field"),
        description=_("Displayed on the Files Submission page."),
        is_translatable=True
    )

    SettingValue.objects.create(
        journal=None,
        setting=submission_figures_data_title,
        value="Figures and Data Files",
        value_cy="Figures and Data Files",  # TODO Fixme!
        value_de="Figures and Data Files",  # TODO Fixme!
        value_en="Figures and Data Files",
        value_fr="Figures and Data Files",  # TODO Fixme!
        value_nl="Figures and Data Files",  # TODO Fixme!
    )


class Migration(migrations.Migration):

    dependencies = [
        ('jcom_profile', '0003_jcomprofile_invitation_token'),
    ]

    operations = [
        migrations.RunPython(add_submission_figures_data_title),
    ]