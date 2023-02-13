"""Data Extraction Titles"""
from journal import models as journal_models
from utils.logger import get_logger
from django.core.management.base import BaseCommand
from submission.models import Article
from identifiers import models as identifier_models
import csv

logger = get_logger(__name__)

class Command(BaseCommand):
    help = "Extract Titles"  # NOQA


    def handle(self, *args, **options):
        """Command entry point."""
        self.options = options
        article_id = ''
        article_id = options["id"]
        #logger.warning(options)
        writer = csv.writer(self.stdout, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['id', 'pubid', 'title'])
        query_set = Article.objects.all().filter(identifier__id_type='pubid').values("id", "title", "identifier__identifier")
        if article_id:
            query_set = Article.objects.all().filter(identifier__id_type='pubid',
                                                     identifier__identifier=article_id).values("id", "title", "identifier__identifier")
        for item in query_set:
          writer.writerow([str(item['id']), str(item['identifier__identifier']), str(item['title'])])

            
    def add_arguments(self, parser):
        """Add arguments to command."""
        parser.add_argument(
            "--id",
            help='Pubication ID of the article to process (e.g. "JCOM_2106_2022_A01").'
            " If not given, all articles are queried and processed.",
        )

