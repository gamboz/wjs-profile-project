"""Data Extraction"""
from journal import models as journal_models
from utils.logger import get_logger
from django.core.management.base import BaseCommand
from submission.models import Article
from core.models import Account
from identifiers import models as identifier_models
import csv
import os
from pytz import timezone

logger = get_logger(__name__)

class Command(BaseCommand):
    help = "Extract Data"  # NOQA


    def handle(self, *args, **options):
        """Command entry point."""
        self.options = options
        #logger.warning(options)
        base_path = ''
        base_path = options["base_path"]
        if base_path:
            article_id = ''
            article_id = options["id"]
            dir_path=''
            if os.path.exists(base_path) and os.path.isdir(base_path):
                dir_path=os.path.join(str(base_path), '')
                self.extract_titles(dir_path, article_id)
                self.extract_abstracts(dir_path, article_id)
                self.extract_keywords(dir_path, article_id)
                self.extract_pubid_doi(dir_path, article_id)
                self.extract_date_published(dir_path, article_id)
                self.extract_corr_auth(dir_path, article_id)
            else:
               self.stdout.write(self.style.ERROR("\nPARAMETERS ERROR: directory not existing \n\n --base-path " + base_path  +  "\n\n "))
        else:
            self.stdout.write(self.style.ERROR("\nPARAMETERS ERROR: the data files destination directory (existing) is a mandatory option:\n\nExample:\n--base-path /home/user1/tmp/ \n\n"))
       
            
    def add_arguments(self, parser):
        """Add arguments to command."""
        parser.add_argument(
            "--id",
            help='Pubication ID of the article to process (e.g. "JCOM_2106_2022_A01").'
            " If not given, all articles are queried and processed.",
        )
        parser.add_argument(
            "--base-path",
            help='Base PATH for data file extracted.'
            " If not given, output is redirect on STDOUT.",
        )


    def extract_titles(self, dir_path, article_id):
        """ extract titles """
        file_name = 'extract_titles.csv'
        if article_id:
           file_name =  'extract_titles_' + article_id.replace(' ', '_') + '.csv'
        with open(dir_path + file_name, 'w', newline='') as titles_csvfile:
            writer = csv.writer(titles_csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(['id', 'pubid', 'title'])
            if article_id:
                query_set = Article.objects.all().filter(identifier__id_type='pubid',
                                                     identifier__identifier=article_id).values("id", "title", "identifier__identifier")
            else:
                query_set = Article.objects.all().filter(identifier__id_type='pubid').values("id", "title", "identifier__identifier")
            for item in query_set:
                    writer.writerow([str(item['id']), str(item['identifier__identifier']), str(item['title'])])
        titles_csvfile.close()

            
    def extract_abstracts(self,  dir_path, article_id):
        """ extract abstracts """
        file_name = 'extract_abstracts.csv'
        if article_id:
           file_name =  'extract_abstracts_' + article_id.replace(' ', '_') + '.csv'
        with open(dir_path + file_name, 'w', newline='') as abstracts_csvfile:
            writer = csv.writer(abstracts_csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(['id', 'pubid', 'abstract'])
            if article_id:
                query_set = Article.objects.all().filter(identifier__id_type='pubid',
                                                     identifier__identifier=article_id).values("id", "abstract", "identifier__identifier")
            else:
                query_set = Article.objects.all().filter(identifier__id_type='pubid').values("id", "abstract", "identifier__identifier")
            for item in query_set:
                writer.writerow([str(item['id']), str(item['identifier__identifier']), str(item['abstract'])])
        abstracts_csvfile.close()
            

    def extract_keywords(self,  dir_path, article_id):
        """ extract keywords """
        file_name = 'extract_keywords.csv'
        if article_id:
           file_name =  'extract_keywords_' + article_id.replace(' ', '_') + '.csv'
        with open(dir_path + file_name, 'w', newline='') as keywords_csvfile:
            writer = csv.writer(keywords_csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(['id', 'pubid', 'keywords'])
            if article_id:
                query_set = Article.objects.all().filter(identifier__id_type='pubid',
                                                     identifier__identifier=article_id).order_by('id').values("id", "keywords__word", "identifier__identifier")
            else:
                query_set = Article.objects.all().filter(identifier__id_type='pubid').order_by('id').values("id", "keywords__word", "identifier__identifier")
            for item in query_set:
                writer.writerow([str(item['id']), str(item['identifier__identifier']), str(item['keywords__word'])])
        keywords_csvfile.close()


    def extract_pubid_doi(self,  dir_path, article_id):
        """ extract pubid doi """
        file_name = 'extract_pubid_doi.csv'
        if article_id:
           file_name =  'extract_pubid_doi_' + article_id.replace(' ', '_') + '.csv'
        with open(dir_path + file_name, 'w', newline='') as pubid_doi_csvfile:
            writer = csv.writer(pubid_doi_csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(['article_id', 'pubid', 'doi'])
            query_set = Article.objects.all().order_by('id')
            for article in query_set:
                if article_id:
                    if  article_id==article.get_identifier('pubid'):
                        writer.writerow([article.id, article.get_identifier('pubid'), article.get_identifier('doi')])
                else:
                    writer.writerow([article.id, article.get_identifier('pubid'), article.get_identifier('doi')])
        pubid_doi_csvfile.close()


    def extract_date_published(self,  dir_path, article_id):
        """ extract published """
        file_name = 'extract_date_published.csv'
        if article_id:
           file_name =  'extract_date_published_' + article_id.replace(' ', '_') + '.csv'
        rome_tz = timezone('Europe/Rome')
        with open(dir_path + file_name, 'w', newline='') as date_published_csvfile:
            writer = csv.writer(date_published_csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(['article_id', 'pubid', 'date_published'])
            query_set = Article.objects.all()
            if article_id:
                for article in query_set:
                    if article_id==article.get_identifier('pubid'):
                        writer.writerow([article.id, article.get_identifier('pubid'), article.date_published.astimezone(tz=rome_tz)])
            else:                
                for article in query_set:
                    writer.writerow([article.id, article.get_identifier('pubid'), article.date_published.astimezone(tz=rome_tz)])
        date_published_csvfile.close()


    def extract_corr_auth(self,  dir_path, article_id):
        """ extract corr_auth """
        file_name = 'extract_corr_auth.csv'
        if article_id:
           file_name =  'extract_corr_auth_' + article_id.replace(' ', '_') + '.csv'
        with open(dir_path + file_name, 'w', newline='') as corr_auth_csvfile:
            writer = csv.writer(corr_auth_csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(['article_id', 'pubid', 'corr_auth_last_name', 'corr_auth_first_name', 'corr_auth_email'])
            query_set = Article.objects.all()
            for article in query_set:
                last_name = ''
                first_name = ''
                email = ''
                if article.correspondence_author:
                    last_name = article.correspondence_author.last_name
                    first_name = article.correspondence_author.first_name
                    email = article.correspondence_author.email
                if article_id:
                    if article_id==article.get_identifier('pubid'):
                        writer.writerow([article.id, article.get_identifier('pubid'), last_name, first_name, email])
                else:                
                    writer.writerow([article.id, article.get_identifier('pubid'), last_name, first_name, email])
        corr_auth_csvfile.close()
