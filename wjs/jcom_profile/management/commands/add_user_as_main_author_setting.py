from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _

from core.models import Setting, SettingValue, SettingGroup


class Command(BaseCommand):
    help = "Create setting to decide whatever the user is the correspondence author when an article is submitted. "

    def _create_user_as_main_author_setting(self, group: SettingGroup):
        user_main_author_setting, setting_created = Setting.objects.get_or_create(
            name="user_automatically_main_author",
            group=group,
            types="boolean",
            pretty_name=_("User automatically as main author"),
            description=_(
                "If true, the submitting user is set as main author. To work, the setting 'user_automatically_author' must be on."),
            is_translatable=False
        )
        try:
            SettingValue.objects.get(journal=None,
                                     setting=user_main_author_setting)
            self.stdout.write(
                self.style.WARNING(
                    "User as main author setting already exists. Do nothing."))
        except SettingValue.DoesNotExist:
            SettingValue.objects.create(
                journal=None,
                setting=user_main_author_setting,
                value=""
            )
            self.stdout.write(
                self.style.SUCCESS(
                    "Successfully created user_as_main_author setting."))

    def _get_group(self, name: str) -> SettingGroup:
        try:
            return SettingGroup.objects.get(name=name)
        except SettingGroup.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"{name} group does not exist."))
            return None

    def handle(self, *args, **options):
        general_settings_group = self._get_group("general")

        if general_settings_group:
            self._create_user_as_main_author_setting(general_settings_group)
        else:
            # TODO: Create an ad hoc command to handle this case? I don't know if it could happen.
            self.stdout.write(
                self.style.ERROR(f"Check out your groups (general) settings before."))
