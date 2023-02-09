"""Data Extraction Titles"""
from journal import models as journal_models
from utils.logger import get_logger
from django.core.management.base import BaseCommand
from submission.models import Article

logger = get_logger(__name__)

class Command(BaseCommand):
    help = "Extract Titles"  # NOQA


    def handle(self, *args, **options):
        """Command entry point."""
        self.options = options
        logger.warning(options)
        logger.warning(Article.objects.all().values("title"))
        
    def add_arguments(self, parser):
        """Add arguments to command."""
        parser.add_argument(
            "--id",
            help='Pubication ID of the article to process (e.g. "JCOM_2106_2022_A01").'
            " If not given, all articles are queried and processed.",
        )

