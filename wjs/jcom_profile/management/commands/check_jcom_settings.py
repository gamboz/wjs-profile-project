"""Check (and/or set) Janeway settings suitable for JCOM."""
from django.core.management.base import BaseCommand
from journal.models import Journal
from press.models import Press
from utils import setting_handler
from utils.logger import get_logger

logger = get_logger(__name__)
VALUE = "CHECK ME!"


class Command(BaseCommand):
    help = "Check (and/or set) Janeway settings suitable for a journal"  # noqa

    def handle(self, *args, **options):
        """Command entry point."""
        self.journal = Journal.objects.get(code=options["journal_code"])
        self.options = options
        self.set_journal_settings()
        self.set_journal_attributes()
        self.set_press_attributes()

    def set_journal_settings(self):
        """Take care of the journal settings."""
        jcom_settings = [
            #
            # Collection Name - Overrides the term "Collections" across all the templates.
            ("general", "collection_name", "Special Issue"),
            #
            # Collection Name Plural - Overrides the term
            # "Collections" across all the templates.
            ("general", "collection_name_plural", "Special Issues"),
            #
            # Copyright Notice - Displayed on the About and Submission
            # pages. You should update this to display the Journal's
            # copyright requirements.
            # TBV: ("general", "copyright_notice", VALUE),
            #
            # Crossref Date Suffix - For migrated content where we
            # need to tweak the crossref date.
            # TBV: ("crossref", "crossref_date_suffix", VALUE),
            #
            # Crossref depositor email - The email of the depositor
            # for this journal on Crossref's system.
            ("Identifiers", "crossref_email", "sysadmin@medialab.sissa.it"),
            #
            # Crossref depositor name - The name of the depositor for
            # this journal on Crossref's system.
            ("Identifiers", "crossref_name", "Sissa Medialab"),
            #
            # Crossref password - The password to log in to Crossref's deposit API.
            ("Identifiers", "crossref_password", "PLEASE SET MANUALLY!"),
            #
            # Crossref prefix - The prefix for this journal on Crossref's system.
            ("Identifiers", "crossref_prefix", "10.22323"),
            #
            # Crossref registrant name - The name of the registrant
            # for this journal on Crossref's system.
            ("Identifiers", "crossref_registrant", "Sissa Medialab"),
            #
            # Use Crossref test deposit server - Whether or not to use
            # Crossref's test server.
            ("Identifiers", "crossref_test", ""),
            #
            # Crossref username - The username to log in to Crossref's deposit API.
            ("Identifiers", "crossref_username", "sissa"),
            #
            # Default Journal Language - The default language for the journal.
            ("general", "default_journal_language", "en"),
            #
            # Disable article large image - If checked, the article
            # large image will not be displayed on the article page
            ("article", "disable_article_large_image", "on"),
            #
            # Disable article thumbnails - If checked, no article
            # thumbnails will be rendered on public article lists
            ("article", "disable_article_thumbnails", "on"),
            #
            # Disable Submission - If true, users cannot submit new articles.
            ("general", "disable_journal_submission", "on"),
            #
            # Disabled Submission Message - A message that is
            # displayed when Disable Submission is on.
            # TBV: ("general", "disable_journal_submission_message", VALUE),
            #
            # Display Altmetric Badges - If enabled altmetric badges
            # will be displayed in the sidebar.
            ("article", "display_altmetric_badge", ""),
            #
            # DOI display prefix - Text to prepend to DOIs. Also used to generate URLs.
            ("Identifiers", "doi_display_prefix", "https://doi.org/"),
            #
            # DOI display suffix - Text to append to DOIs. Also used to generate URLs.
            ("Identifiers", "doi_display_suffix", ""),
            #
            # Article DOI Pattern - You can set your DOI pattern. The
            # default is ``{{ article.journal.code }}.{{ article.pk
            # }}``
            ("Identifiers", "doi_pattern", "2.WRITEME"),  # e.g. 2.22010703
            #
            # Embargo Period (KBART) - Optional period of embargo this
            # journal is subject to. It must follow the kbart format
            # such as 'R2Y' or 'P1Y'
            # TBV: ("kbart", "embargo_period", VALUE),
            #
            # Enable Crosscheck - If enabled, links to crosscheck reports will be displayed
            ("crosscheck", "enable", ""),
            #
            # Enable Editorial Team Display - If checked, editorial team link will display in Navigation
            ("general", "enable_editorial_display", ""),
            #
            # Enable Editorial Team Image Display - If checked, Editorial Team images will display.
            ("styling", "enable_editorial_images", ""),
            #
            # Focus and Scope - Journal's Focus and Scope, displayed on the Submissions page.
            # TBV: ("general", "focus_and_scope", VALUE),
            #
            # From Address - System emails are sent From this address.
            ("general", "from_address", "jcom-eo@jcom.sissa.it"),
            #
            # Hide Author Email Links - If enabled the article page
            # will not display links to email correspondence authors.
            ("article", "hide_author_email_links", ""),
            #
            # Journal Uses HTTPS - Used for URL generation.
            ("general", "is_secure", "on"),
            #
            # Journal Base Theme - When using a custom theme you can
            # set the base theme, when a template from a custom theme
            # is missing templates from the base theme will be used as
            # a backup.
            ("general", "journal_base_theme", "material"),
            #
            # Journal Description - Localised description of the journal.
            (
                "general",
                "journal_description",
                "The Journal of Science Communication (JCOM) is a diamond open access,"
                " peer reviewed journal focused on science communication."
                " The Journal covers a broad range of issues pertinent to science communication"
                " and public engagement with STEM, including citizen science"
                " as well as environmental and health communication,"
                " where these relate to communication of research. ",
            ),
            #
            # Journal ISSN - The ISSN of the journal.
            ("general", "journal_issn", "1824-2049"),
            #
            # TODO: broken in 1.4, fixed in 1.5 - see thread on Discord
            # Journal Languages - Languages available for this journal.
            # Just ignore for now: ("general", "journal_languages", ["en"]),
            #
            # Journal Name - Name of the journal.
            ("general", "journal_name", "Journal of Science Communication"),
            #
            # Journal Theme - The HTML theme set to use for the journal.
            ("general", "journal_theme", "JCOM-theme"),
            #
            # Enable the Keyword list page - Lists all of the keywords
            # used by a journal and for each keyword a list of
            # articles that use it.
            ("general", "keyword_list_page", "on"),
            #
            # Main Contact - Primary contact for the journal.
            # TBV: ("general", "main_contact", VALUE),
            #
            # Matomo Tracking Code - Tracking code for Matomo.
            ("general", "matromo_tracking_code", "WRITEME! #120"),
            #
            # News Title - Title for the News Page and Homepage block
            ("news", "news_title", "News"),
            #
            # Number of Articles - Number of news articles to display on the homepage.
            ("plugin:News", "number_of_articles", "11"),
            #
            # Number of Most Popular Articles to Display - Determines
            # how many popular articles we should display.
            ("plugin:Popular Articles", "num_most_popular", "10"),
            #
            # Print ISSN - The ISSN of the printed version of the journal.
            ("general", "print_issn", ""),
            #
            # External Privacy Policy URL - URL to an external
            # privacy-policy, linked from the footer. If blank, it
            # links to the Janeway CMS page: /site/privacy.
            ("general", "privacy_policy_url", "https://medialab.sissa.it/privacy"),
            #
            # Publication Fees - Display of feeds for this
            # journal. Displayed on the About and the Submission
            # pages.
            # TBV: ("general", "publication_fees", VALUE),
            #
            # Publisher Name - Name of the Journal's
            # Publisher. Displayed throughout the site and metadata.
            ("general", "publisher_name", "Sissa Medialab"),
            #
            # Publisher URL - URL of the Journal's Publisher.
            ("general", "publisher_url", "https://medialab.sissa.it/"),
            #
            # Reader Publication Notification - Email sent readers
            # when new articles are published.
            # Not used: ("email", "reader_publication_notification", VALUE),
            # Don't confuse with `subscribe_custom_email_message`
            #
            # Auto-register issue-level DOIs - Automatically register
            # issue DOIs on article publication, based on the issue
            # DOI pattern
            ("Identifiers", "register_issue_dois", ""),
            #
            # Reply-To Address - Address set as the 'Reply-to' for system emails.
            ("general", "replyto_address", ""),
            #
            # Send Reader Notifications - If enabled Janeway will
            # notify readers of new published articles.
            # Not used: ("notifications", "send_reader_notifications", VALUE),
            # Don't confuse with `subscribe_custom_email_message` (no enable/disable flag)
            #
            # Subject Reader Publication Notification - Subject for
            # Submission Access Request Complete.
            # Not used: ("email_subject", "subject_reader_publication_notification", VALUE),
            # Don't confuse with `subscribe_custom_email_message` (subject hardcoded)
            #
            # Submission Checklist - Displayed on the About and
            # Submission pages. You should update this with an ordered
            # list of submission requirements.
            # TBV: ("general", "submission_checklist", VALUE),
            #
            # Email message that is sent when an anonymous user
            # subscribes to newsletters. - Message email body
            (
                "email",
                "subscribe_custom_email_message",
                "Hi,\nYou requested to subscribe to {} journal newsletters.\n"
                "To continue click the following link:{}",
            ),
            # See also wjs/jcom_profile/management/commands/add_custom_subscribe_email_message_settings.py
            #
            # Janeway Support Contact for Staff - Support message to
            # display to editors and staff on Manager page.
            # TBV: ("general", "support_contact_message_for_staff", VALUE),
            #
            # Support Email - Support email address for editors and staff users.
            ("general", "support_email", "gamboz@medialab.sissa.it"),
            #
            # Suppress Citation Metrics - If enabled this will
            # suppress the citations counter on the article page. The
            # citation block will only appear for articles that have a
            # citation. This setting is overruled by the Disable
            # Metrics setting.
            ("article", "suppress_citations_metric", "on"),
            #
            # Suppress How to Cite - If enabled this will suppress the
            # how to cite block on the article page.
            ("article", "suppress_how_to_cite", ""),
            #
            # Switch Language - Allow users to change their language.
            ("general", "switch_language", ""),
            #
            # Twitter Handle - Journal's twitter handle.
            ("general", "twitter_handle", "https://twitter.com/JsciCOM"),
            #
            # Use Crossref DOIs - Whether or not to use Crossref DOIs.
            ("Identifiers", "use_crossref", "on"),
            #
            # Use Google Analytics 4 - Use cookieless GA 4 instead of traditional analytics.
            ("general", "use_ga_four", ""),
        ]

        for group_name, setting_name, value in jcom_settings:
            current_value = setting_handler.get_setting(
                group_name,
                setting_name,
                self.journal,
                create=False,
                default=True,
            )
            current_value = current_value and current_value.value or None
            if self.options["force"]:
                if current_value and current_value != value:
                    logger.debug(f'Forcing {setting_name} to "{value}" (was "{current_value}")')
                setting_handler.save_setting(group_name, setting_name, self.journal, value)
            elif self.options["check_only"]:
                if current_value and current_value != value:
                    self.notice(f'Setting {setting_name} is "{current_value}" vs. expected "{value}"')
            else:
                raise Exception("Come sei arrivato qui?! qualcuno mi ha cambiato le opzioni??? 😠")

    def set_press_attributes(self):
        """Take care of the Press attibutes."""
        attributes = (
            ("main_contact", "eo@medialab.sissa.it"),
            ("name", "SISSA Journals"),
        )
        press = Press.objects.get()
        press_changed = False
        for attribute, value in attributes:
            if not hasattr(press, attribute):
                self.error(f"Press {press} has not attribute {attribute}!")
                continue
            current_value = getattr(press, attribute)
            if self.options["force"]:
                if current_value != value:
                    logger.debug(f'Forcing press.{attribute} to "{value}" (was "{current_value}")')
                setattr(press, attribute, value)
                press_changed = True
            elif self.options["check_only"]:
                if current_value != value:
                    self.notice(f'Press.{attribute} is "{current_value}" vs. expected "{value}"')
            else:
                raise Exception("Come sei arrivato qui?! qualcuno mi ha cambiato le opzioni??? 😠")
        if press_changed:
            press.save()

    def set_journal_attributes(self):
        """Take care of the Journal attibutes."""
        attributes = (
            ("display_article_number", False),
            ("display_article_page_numbers", False),
            ("display_issue_doi", False),
            ("display_issue_number", True),
            ("display_issue_title", True),
            ("display_issue_volume", True),
            ("display_issue_year", True),
        )
        journal = self.journal
        journal_changed = False
        for attribute, value in attributes:
            if not hasattr(journal, attribute):
                self.error(f"Journal {journal} has not attribute {attribute}!")
                continue
            current_value = getattr(journal, attribute)
            if self.options["force"]:
                if current_value != value:
                    logger.debug(f'Forcing journal.{attribute} to "{value}" (was "{current_value}")')
                setattr(journal, attribute, value)
                journal_changed = True
            elif self.options["check_only"]:
                if current_value != value:
                    self.notice(f'Journal.{attribute} is "{current_value}" vs. expected "{value}"')
            else:
                raise Exception("Come sei arrivato qui?! qualcuno mi ha cambiato le opzioni??? 😠")
        if journal_changed:
            journal.save()

    def notice(self, msg):
        """Emit a notice."""
        self.stdout.write(self.style.NOTICE(msg))

    def error(self, msg):
        """Emit an error."""
        self.stdout.write(self.style.ERROR(msg))

    def add_arguments(self, parser):
        """Add arguments to command."""
        behavior = parser.add_mutually_exclusive_group(required=True)
        behavior.add_argument(
            "--check-only",
            action="store_true",
            help="Just report the situation: do not set anything.",
        )
        behavior.add_argument(
            "--force",
            action="store_true",
            help="Set all. By default, we don't change anything that is different from the default/unset state",
        )
        parser.add_argument(
            "--journal-code",
            default="JCOM",
            help="The code of the journal that we are working on. Defaults to $(default)s.",
        )
