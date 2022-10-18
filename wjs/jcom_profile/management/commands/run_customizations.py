from django.core import management
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run all customizations implemented as django-admin commands"  # NOQA

    def handle(self, *args, **options):
        management.call_command("add_coauthors_submission_email_settings")
