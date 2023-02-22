"""Data migration POC."""
import datetime
import os
import pathlib
import sys
import tempfile
import time
import zipfile

from core.models import Account
from django.core.management.base import BaseCommand
from identifiers import models as identifiers_models
from journal import models as journal_models
from lxml import etree
from submission import models as submission_models
from utils.logger import get_logger
from watchdog.events import LoggingEventHandler
from watchdog.observers import Observer

from wjs.jcom_profile import models as wjs_models
from wjs.jcom_profile.import_utils import query_wjapp_by_pubid, set_author_country
from wjs.jcom_profile.management.commands.import_from_drupal import (
    NON_PEER_REVIEWED,
    SECTION_ORDER,
    rome_timezone,
)
from wjs.jcom_profile.utils import from_pubid_to_eid

# , set_language
# JANEWAY_LANGUAGES_BY_CODE = ...

# Map wjapp article types to Janeway section names
SECTIONS_MAPPING = {
    "editorial": "Editorial",
    "article": "Article",
    "review article": "Review Article",
    "practice insight": "Practice insight",
    "essay": "Essay",
    "focus": "Focus",
    "commentary": "Commentary",
    "comment": "Commentary",  # comment ↔ commentary
    "letter": "Letter",
    "book review": "Book Review",
    "conference review": "Conference Review",
}


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
        # TODO: apply fixer4xml.py

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
        article.refresh_from_db()

        # Keywords
        # Drop all article's kwds (and KeywordArticles, used for kwd ordering)
        article.keywords.clear()
        for order, kwd_obj in enumerate(xml_obj.findall("//document/keyword")):
            # Janeway's keywords are a simple model with a "word" field for the kwd text
            kwd_word = kwd_obj.text.strip()
            keyword, created = submission_models.Keyword.objects.get_or_create(word=kwd_word)
            if created:
                logger.warning('Created keyword "{kwd_word}" for {pubid}. Kwds are not ofter created. Please check!')
            submission_models.KeywordArticle.objects.get_or_create(
                article=article,
                keyword=keyword,
                order=order,
            )
            logger.debug(f"Keyword {kwd_word} set at order {order}")
            article.keywords.add(keyword)
        article.save()

        # Issue / volume
        # wjapp's XML has the same info in several places. Let's do some sanity check.
        vol_obj_a = xml_obj.find("//volume")
        vol_obj_b = xml_obj.find("//document/volume")
        issue_obj_a = xml_obj.find("//issue")
        issue_obj_b = xml_obj.find("//document/issue")
        volume = vol_obj_a.get("volumeid")
        issue = issue_obj_a.get("issueid")
        if vol_obj_a.get("volumeid") != vol_obj_b.get("volumeid"):
            logger.error(f"Mismatching volume ids for {pubid}. Using {volume}")
        if issue_obj_a.get("issueid") != issue_obj_b.get("issueid"):
            logger.error(f"Mismatching issue ids for {pubid}. Using {issue}")
        # The first issue element also has a reference to the volumeid...
        if issue_obj_a.get("volumeid") != volume:
            logger.error(f"Mismatching issue/volume ids for {pubid}.")
        if not issue.startswith(volume):
            logger.error(f'Unexpected issueid "{issue}". Trying to proceed anyway.')

        issue = issue.replace(volume, "")
        issue = int(issue)
        volume = int(volume)

        # More sanity check: the volume's title always has the form
        # "Volume 01, 2002"
        volume_title = vol_obj_a.text
        year = 2001 + volume
        if volume_title != f"Volume {volume:02}, {year}":
            logger.error(f'Unexpected volume title "{volume_title}"')

        # If the issue's text has a form different from
        # "Issue 01, 2023"
        # then it's a special issue (aka "collection")
        issue_type__code = "issue"
        issue_title = ""
        if "Special" in issue_obj_a.text:
            logger.warning(f'Unexpected issue title "{issue_title}", consider this a "special issue"')
            issue_type__code = "collection"
            issue_title = issue_obj_a.text

        issue, created = journal_models.Issue.objects.get_or_create(
            journal=jcom,
            volume=volume,
            issue=issue,
            issue_type__code=issue_type__code,
            defaults={
                "date": article.date_published,  # ⇦ delicate
                "issue_title": issue_title,
            },
        )

        issue.issue_title = issue_title

        if created:
            issue_type = journal_models.IssueType.objects.get(
                code=issue_type__code,
                journal=jcom,
            )
            issue.issue_type = issue_type
            issue.save()

        issue.save()

        # not needed(?): journal_models.SectionOrdering.objects.filter(issue=issue).delete()
        section_name = xml_obj.find("//document/type").text
        if section_name not in SECTIONS_MAPPING:
            logger.critical(f'Unknown article type "{section_name}" for {pubid}')
            sys.exit(1)
        section_name = SECTIONS_MAPPING.get(section_name)

        section, created = submission_models.Section.objects.get_or_create(
            journal=article.journal,
            name=section_name,
        )
        if created:
            logger.warning(
                'Created section "{section_name}" for {pubid}. Sections are not ofter created. Please check!',
            )

        article.section = section

        if article.section.name in NON_PEER_REVIEWED:
            article.peer_reviewed = False

        # Must ensure that a SectionOrdering exists for this issue,
        # otherwise issue.articles.add() will fail.
        #
        section_order = SECTION_ORDER[section.name]
        journal_models.SectionOrdering.objects.get_or_create(
            issue=issue,
            section=section,
            defaults={"order": section_order},
        )

        article.primary_issue = issue
        article.save()
        issue.articles.add(article)
        issue.save()
        logger.debug(f"Issue {issue.volume}({issue.issue}) set for {pubid}")

        # Authors
        self.set_authors(article, xml_obj)

        # License (always the same)
        article.license = submission_models.Licence.objects.get(short_name="CC BY-NC-ND 4.0")
        article.save()

    def set_authors(self, article, xml_obj):
        """Find and set the article's authors, creating them if necessary."""
        # The "source" of this author's info, used for future reference
        wjapp = query_wjapp_by_pubid(article.get_identifier("pubid"))
        source = "jcom"
        pubid = article.get_identifier("pubid")
        # The first set of <author> elements (the one outside
        # <document>) is guarantee to have the names and the order
        # correct. Ignore the rest (beware "//author" != "/author")
        for order, author_obj in enumerate(xml_obj.findall("/author")):
            # Don't confuse user_cod (camelcased originally) that is
            # the pk of the user in wjapp with Account.id in Janeway.
            user_cod = author_obj.get("authorid")
            email = author_obj.get("email")
            if not email:
                email = f"{user_cod}@invalid.com"
                logger.error(f"No email for author {user_cod} on {pubid}. Using {email}")
            # just in case:
            email = email.strip()
            author, created = Account.objects.get_or_create(
                usercods__source=source,
                usercods__user_cod=user_cod,
                defaults={
                    "email": email,
                    "first_name": author_obj.get("firstname"),  # NB: this contains first+middle
                    "last_name": author_obj.get("lastname"),
                },
            )
            if created:
                # Store info about where this author came from, so we
                # can match him in the future.
                mapping, _ = wjs_models.Correspondence.objects.get_or_create(
                    account=author,
                    user_cod=user_cod,
                    source=source,
                )
                # `used` indicates that this usercod from this source
                # has been used to create the core.Account record
                mapping.used = True
                mapping.save()

            author.add_account_role("author", article.journal)

            # Add authors to m2m and create an order record
            article.authors.add(author)
            order, _ = submission_models.ArticleAuthorOrder.objects.get_or_create(
                article=article,
                author=author,
                order=order,
            )

        # Set the primary author
        corresponding_author_usercod = wjapp.get("userCod")  # Expect to alway find something!
        mapping = wjs_models.Correspondence.objects.get(user_cod=corresponding_author_usercod, source=source)
        main_author = mapping.account
        set_author_country(main_author, wjapp)
        article.owner = main_author
        article.correspondence_author = main_author
        article.save()
        logger.debug(f"Set {article.authors.count()} authors onto {pubid}")

    #     # Set the PDF file as a galley of the Article
    #     # Generate the full-text html from the TeX sources
    # # import jcomassistant
    # # html_file: Path = jcomassistant.mkft(cwd)
    #     # Set the full-text html as the render_galley of the article
    #     # Generate the EPUB from the TeX sources
    # # epub_file: Path = jcomassistant.mkepub(html_file, publication_year, number, issue, type)
    #     # Set the EPUB file as a galley of the Article
    #     # Cleanup
    #     shutil.rmtree(tmpdir)
