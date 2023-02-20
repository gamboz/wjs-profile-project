"""Data migration POC."""
import datetime
import os
import pathlib
import shutil
import sys
import tempfile
import time
import zipfile

from django.core.management.base import BaseCommand
from identifiers import models as identifiers_models
from journal import models as journal_models
from lxml import etree
from submission import models as submission_models
from utils.logger import get_logger
from watchdog.events import LoggingEventHandler
from watchdog.observers import Observer

from wjs.jcom_profile import models as wjs_models
from wjs.jcom_profile.management.commands.import_from_drupal import (
    COUNTRIES_MAPPING,
    NON_PEER_REVIEWED,
    rome_timezone,
)
from wjs.jcom_profile.utils import from_pubid_to_eid

# , set_language
# JANEWAY_LANGUAGES_BY_CODE = ...


logger = get_logger(__name__)

WATCH_DIR = pathlib.Path("/tmp/wjapp-wjs")


class Command(BaseCommand):
    help = "Import an article from wjapp."  # NOQA

    def handle(self, *args, **options):
        """Command entry point."""
        self.options = options
        # Not yet: self.start_watchdog()
        self.read_from_watched_dir()

    def add_arguments(self, parser):
        """Add arguments to command."""
        parser.add_argument(
            "--writeme",
            action="store_true",
            help="Do smth.",
        )

    def start_watchdog(self):
        """Start the watchdog (if it's not yet running)."""
        logger.error("Watchdog not implemented!")
        sys.exit(1)
        event_handler = LoggingEventHandler()
        observer = Observer()

        observer.schedule(event_handler, WATCH_DIR)
        observer.start()
        try:
            while observer.is_alive():
                observer.join(1)
        finally:
            observer.stop()
            observer.join()
            logger.info("Watchdog stopped for %s", WATCH_DIR)

    def read_from_watched_dir(self):
        """Read zip files from the watched folder and start the import process."""
        files = os.listdir(WATCH_DIR)
        for zip_file in files:
            self.process(WATCH_DIR / zip_file)

    def process(self, zip_file):
        """Uncompress the zip file, and create the importing Article from the XML metadata."""
        # Wait for the file to be finished writing to.
        # Add 1 sec. overhead, but it's insubstantial
        logger.debug(f"Looking at {zip_file}")
        mtime_t0 = os.stat(zip_file).st_mtime
        while True:
            time.sleep(1)
            mtime_t1 = os.stat(zip_file).st_mtime
            if mtime_t1 == mtime_t0:
                break
        # Unzip in a temporary dir
        tmpdir = tempfile.mkdtemp()
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(tmpdir)
        # Expect to find one XML and one PDF file
        xml_files = list(pathlib.Path(tmpdir).rglob("*.xml"))
        if len(xml_files) == 0:
            logger.critical(f"No XML file found in {zip_file}. Quitting and leaving a mess...")
            sys.exit(1)
        if len(xml_files) > 1:
            logger.warning("Found {len(xml_file)} XML files in {zip_file}. Using the first one {xml_files[0]}")
        xml_file = xml_files[0]

        pdf_files = list(pathlib.Path(tmpdir).rglob("*.pdf"))
        if len(pdf_files) == 0:
            logger.critical(f"No PDF file found in {zip_file}. Quitting and leaving a mess...")
            sys.exit(1)
        if len(pdf_files) > 1:
            logger.warning("Found {len(pdf_file)} PDF files in {zip_file}. Using the first one {pdf_files[0]}")
        pdf_file = pdf_files[0]

        # Read the XML file and create an Article
        xml_obj = etree.parse(xml_file)

        pubid = xml_obj.find("//document/articleid").text
        jcom = journal_models.Journal.objects.get(code="JCOM")
        logger.debug(f"Creating {pubid}")
        article = submission_models.Article.get_article(
            journal=jcom,
            identifier_type="pubid",
            identifier=pubid,
        )
        if article:
            # This is not the default situation: if we are here it
            # means that the article has been already imported and
            # that we are re-importing.
            logger.warning(f"Re-importing existing article {pubid} at {article.id}")
        else:
            article = submission_models.Article.objects.create(
                journal=jcom,
            )
        article.title = xml_obj.find("//document/title").text
        article.abstract = xml_obj.find("//document/abstract").text
        article.imported = True
        article.date_accepted = rome_timezone.localize(
            datetime.datetime.fromisoformat(xml_obj.find("//document/date_accepted").text),
        )
        article.date_submitted = rome_timezone.localize(
            datetime.datetime.fromisoformat(xml_obj.find("//document/date_submitted").text),
        )
        article.date_published = rome_timezone.localize(
            datetime.datetime.fromisoformat(xml_obj.find("//document/date_published").text),
        )
        article.save()
        identifiers_models.Identifier.objects.get_or_create(
            identifier=xml_obj.find("//document/doi").text,
            article=article,
            id_type="doi",  # should be a member of the set identifiers_models.IDENTIFIER_TYPES
            enabled=True,
        )
        logger.debug(f"Set doi {article.get_doi()} onto {article.pk}")
        identifiers_models.Identifier.objects.get_or_create(
            identifier=pubid,
            article=article,
            id_type="pubid",  # should be a member of the set identifiers_models.IDENTIFIER_TYPES
            enabled=True,
        )
        logger.debug(f"Set pubid {pubid} onto {article.pk}")
        article.page_numbers = from_pubid_to_eid(pubid)
        article.save()
        # TODO:
        # - issue (with volume)
        # - section (mangle names - wjapp has lower case and "comment")
        # - authors (compare with existing)
        # - keywords

        # Set the PDF file as a galley of the Article
        # Get the documentCod or the prePrintId from the publicationId
        # Get the TeX source files
        # Generate the full-text html from the TeX sources
        # Set the full-text html as the render_galley of the article
        # Generate the EPUB from the TeX sources
        # Set the EPUB file as a galley of the Article
        # Cleanup
        shutil.rmtree(tmpdir)
