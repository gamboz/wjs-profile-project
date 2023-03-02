"""Data migration POC."""
import datetime
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

from core.models import Account
from django.core.files import File
from django.core.management.base import BaseCommand
from identifiers import models as identifiers_models
from jcomassistant import make_xhtml
from journal import models as journal_models
from lxml import etree
from production.logic import save_galley, save_supp_file
from submission import models as submission_models
from utils.logger import get_logger
from watchdog.events import LoggingEventHandler
from watchdog.observers import Observer

from wjs.jcom_profile import models as wjs_models
from wjs.jcom_profile.import_utils import (
    decide_galley_label,
    drop_existing_galleys,
    fake_request,
    publish_article,
    query_wjapp_by_pubid,
    set_author_country,
    set_language,
)
from wjs.jcom_profile.management.commands.import_from_drupal import (
    NON_PEER_REVIEWED,
    SECTION_ORDER,
    rome_timezone,
)
from wjs.jcom_profile.utils import from_pubid_to_eid

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


class UnknownSection(Exception):
    pass


logger = get_logger(__name__)

WATCH_DIR = Path("/tmp/wjapp-wjs")


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
        raise Exception()

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
        files = WATCH_DIR.glob("*.zip")
        for zip_file in files:
            self.process(WATCH_DIR / zip_file)

    def process(self, zip_file):
        """Uncompress the zip file, and create the importing Article from the XML metadata."""
        logger.debug(f"Looking at {zip_file}")
        # wjapp provides an "atomic" upload: when the file if present,
        # it is ready and fully uploaded.

        # Unzip in a temporary dir
        tmpdir = Path(tempfile.mkdtemp())
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(tmpdir)

        # Expect to find a folder
        workdir = os.listdir(tmpdir)
        if len(workdir) != 1:
            logger.error(f"Found {len(workdir)} files in the root of the zip file. Trying the first: {workdir[0]}")
        workdir = tmpdir / Path(workdir[0])

        # Expect to find one XML (and some PDF files)
        xml_files = list(workdir.glob("*.xml"))
        if len(xml_files) == 0:
            logger.critical(f"No XML file found in {zip_file}. Quitting and leaving a mess...")
            raise FileNotFoundError(f"No XML file found in {zip_file}")
        if len(xml_files) > 1:
            logger.warning("Found {len(xml_file)} XML files in {zip_file}. Using the first one {xml_files[0]}")
        xml_file = xml_files[0]
        xml_obj = self.preprocess_xmlfile(xml_file)
        article, pubid = self.create_article(xml_obj)
        self.set_keywords(article, xml_obj, pubid)
        issue = self.set_issue(article, xml_obj, pubid)
        self.set_section(article, xml_obj, pubid, issue)
        self.set_authors(article, xml_obj)
        self.set_license(article)
        self.set_pdf_galleys(article, xml_obj, pubid, workdir)
        self.set_supplementary_material(article, pubid, workdir)

        # Generate the full-text html from the TeX sources
        src_folder = workdir / "src"
        if not os.path.exists(src_folder):
            raise FileNotFoundError(f"Missing src folder {src_folder}")
        tex_filenames = list(src_folder.glob("JCOM_*.tex"))
        if len(tex_filenames) > 1:
            logger.warning(f"Found {len(tex_filenames)} tex files. Using {tex_filenames[0]}")
        tex_filename = tex_filenames[0]
        make_xhtml.make(tex_filename)
        # TODO: use the HTML galley

        # Generate the EPUB from the TeX sources
        logger.error("WRITEME: generate and set HTML galley from src files")

        publish_article(article)
        # Cleanup
        shutil.rmtree(tmpdir)

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

    def set_keywords(self, article, xml_obj, pubid):
        """Set the keywords."""
        # Drop all article's kwds (and KeywordArticles, used for kwd ordering)
        article.keywords.clear()
        for order, kwd_obj in enumerate(xml_obj.findall("//document/keyword")):
            # Janeway's keywords are a simple model with a "word" field for the kwd text
            kwd_word = kwd_obj.text.strip()
            keyword, created = submission_models.Keyword.objects.get_or_create(word=kwd_word)
            if created:
                logger.warning('Created keyword "{kwd_word}" for {pubid}. Kwds are not often created. Please check!')
            submission_models.KeywordArticle.objects.get_or_create(
                article=article,
                keyword=keyword,
                order=order,
            )
            logger.debug(f"Keyword {kwd_word} set at order {order}")
            article.keywords.add(keyword)
        article.save()

    def set_issue(self, article, xml_obj, pubid):
        """Set the issue."""
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
            journal=article.journal,
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
                journal=article.journal,
            )
            issue.issue_type = issue_type
            issue.save()

        issue.save()
        return issue

    def set_section(self, article, xml_obj, pubid, issue):
        """Set the section and the section's order in the issue."""
        # not needed(?): journal_models.SectionOrdering.objects.filter(issue=issue).delete()
        section_name = xml_obj.find("//document/type").text
        if section_name not in SECTIONS_MAPPING:
            logger.critical(f'Unknown article type "{section_name}" for {pubid}')
            raise UnknownSection(f'Unknown article type "{section_name}" for {pubid}')
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

    def set_license(self, article):
        """Set the license (always the same)."""
        article.license = submission_models.Licence.objects.get(short_name="CC BY-NC-ND 4.0", journal=article.journal)
        article.save()

    def set_pdf_galleys(self, article, xml_obj, pubid, workdir):
        """Set the PDF galleys: original language and tranlastion."""
        # PDF galleys
        # Should find one file (common case) or two files (original language + english translation)
        pdf_files = list(workdir.glob("*.pdf"))
        if len(pdf_files) == 0:
            logger.critical(f"No PDF file found in {workdir}. Quitting and leaving a mess...")
            raise FileNotFoundError(f"No PDF file found in {workdir}.")
        if len(pdf_files) > 2:
            logger.warning(f"Found {len(pdf_files)} PDF files for {pubid}. Please check.")

        drop_existing_galleys(article)

        # Set default language to English. This will be overridden
        # later if we find a non-English galley.
        #
        # I'm not sure that it is correct to set a language different
        # from English when the doi points to English-only metadata
        # (even if there are two PDF files). But see #194.
        article.language = "eng"

        for pdf_file in pdf_files:
            file_name = os.path.basename(pdf_file)
            file_mimetype = "application/pdf"  # I just know it! (sry :)
            uploaded_file = File(open(pdf_file, "rb"), file_name)
            label, language = decide_galley_label(pubid, file_name=file_name, file_mimetype=file_mimetype)
            if language and language != "en":
                if article.language != "eng":
                    # We can have 2 non-English galleys (PDF and EPUB),
                    # they are supposed to be of the same language. Not checking.
                    #
                    # If the article language is different from
                    # english, this means that a non-English gally has
                    # already been processed and there is no need to
                    # set the language again.
                    pass
                else:
                    set_language(article, language)
            save_galley(
                article,
                request=fake_request,
                uploaded_file=uploaded_file,
                is_galley=True,
                label=label,
                save_to_disk=True,
                public=True,
            )
            logger.debug(f"PDF galley {label} set onto {pubid}")

    def create_article(self, xml_obj):
        """Create the article."""
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
        return (article, pubid)

    def set_supplementary_material(self, article, pubid, workdir):
        """Set supplementary files if necessary."""
        # There is no useful info in wjapp's XML file about
        # supplementary material, so we don't need any reference to
        # the XML file.

        # We might be working on an exiting article, let's cleanup
        for supp_file in article.supplementary_files.all():
            supp_file.file.delete()
            supp_file.file = None
        article.supplementary_files.clear()

        attachments_folder = workdir / "attachments"
        if not os.path.exists(attachments_folder):
            return

        for supplementary_file in os.listdir(attachments_folder):
            file_name = os.path.basename(supplementary_file)
            uploaded_file = File(open(attachments_folder / supplementary_file, "rb"), file_name)
            save_supp_file(
                article,
                request=fake_request,
                uploaded_file=uploaded_file,
                label=file_name,
            )
            logger.debug(f"Supplementary material {file_name} set onto {pubid}")

    def preprocess_xmlfile(self, xml_file):
        """Correct know errors in wjapp XML file.

        - clean up residual TeX fragments from title and abstract
        - correct authors' names
        - re-order authors
        """
        xml_obj = etree.parse(xml_file)
        logger.error("WRITEME: apply fixer4xml.py")
        return xml_obj
