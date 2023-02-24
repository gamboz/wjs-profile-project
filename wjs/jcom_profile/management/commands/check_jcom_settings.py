"""Check (and/or set) Janeway settings suitable for JCOM."""
from django.core.management.base import BaseCommand
from journal.models import Journal
from utils import setting_handler

VALUE = "CHECK ME!"


class Command(BaseCommand):
    help = "Check (and/or set) Janeway settings suitable for JCOM"  # noqa

    def handle(self, *args, **options):
        """Command entry point."""
        jcom = Journal.objects.get(code="JCOM")

        jcom_settings = [
            #
            # Collection Name - Overrides the term "Collections" across all the templates.
            ("general", "collection_name", "Special Issue"),
            #
            # Collection Name Plural - Overrides the term "Collections" across all the templates.
            ("general", "collection_name_plural", "Special Issues"),
            #
            # Copyright Notice - Displayed on the About and Submission
            # pages. You should update this to display the Journal's
            # copyright requirements.
            # TBV: ("general", "copyright_notice", VALUE),
            #
            # Crossref Date Suffix - For migrated content where we need to tweak the crossref date.
            # TBV: ("crossref", "crossref_date_suffix", VALUE),
            #
            # Crossref depositor email - The email of the depositor for this journal on Crossref's system.
            ("Identifiers", "crossref_email", VALUE),
            #
            # Crossref depositor name - The name of the depositor for this journal on Crossref's system.
            ("Identifiers", "crossref_name", VALUE),
            #
            # Crossref password - The password to log in to Crossref's deposit API.
            ("Identifiers", "crossref_password", VALUE),
            #
            # Crossref prefix - The prefix for this journal on Crossref's system.
            ("Identifiers", "crossref_prefix", VALUE),
            #
            # Crossref registrant name - The name of the registrant for this journal on Crossref's system.
            ("Identifiers", "crossref_registrant", VALUE),
            #
            # Use Crossref test deposit server - Whether or not to use Crossref's test server.
            ("Identifiers", "crossref_test", VALUE),
            #
            # Crossref username - The username to log in to Crossref's deposit API.
            ("Identifiers", "crossref_username", VALUE),
            #
            # Default Journal Language - The default language for the journal.
            ("general", "default_journal_language", VALUE),
            #
            # Disable article large image - If checked, the article large image will not be displayed on the article page
            ("article", "disable_article_large_image", VALUE),
            #
            # Disable article thumbnails - If checked, no article thumbnails will be rendered on public article lists
            ("article", "disable_article_thumbnails", VALUE),
            #
            # Disable Submission - If true, users cannot submit new articles.
            ("general", "disable_journal_submission", VALUE),
            #
            # Disabled Submission Message - A message that is displayed when Disable Submission is on.
            ("general", "disable_journal_submission_message", VALUE),
            #
            # Display Altmetric Badges - If enabled altmetric badges will be displayed in the sidebar.
            ("article", "display_altmetric_badge", VALUE),
            #
            # Enable Journal title in Navbar - If checked, the journal title will be displayed on the top bar of the site (not supported on Material theme)
            ("styling", "display_journal_title", VALUE),
            #
            # Display Login Page Notice - If set to true the Login Page Notice will display.
            ("general", "display_login_page_notice", VALUE),
            #
            # DOI display prefix - Text to prepend to DOIs. Also used to generate URLs.
            ("Identifiers", "doi_display_prefix", VALUE),
            #
            # DOI display suffix - Text to append to DOIs. Also used to generate URLs.
            ("Identifiers", "doi_display_suffix", VALUE),
            #
            # DOI Manager Action Maximum Size - Maximum number of articles on which an action can be performed in the DOI Manager
            ("Identifiers", "doi_manager_action_maximum_size", VALUE),
            #
            # Article DOI Pattern - You can set your DOI pattern. The default is ``{{ article.journal.code }}.{{ article.pk }}``
            ("Identifiers", "doi_pattern", VALUE),
            #
            # Embargo Period (KBART) - Optional period of embargo this journal is subject to. It must follow the kbart format such as 'R2Y' or 'P1Y'
            ("kbart", "embargo_period", VALUE),
            #
            # Enable Crosscheck - If enabled, links to crosscheck reports will be displayed
            ("crosscheck", "enable", VALUE),
            #
            # Enable Editorial Team Display - If checked, editorial team link will display in Navigation
            ("general", "enable_editorial_display", VALUE),
            #
            # Enable Editorial Team Image Display - If checked, Editorial Team images will display.
            ("styling", "enable_editorial_images", VALUE),
            #
            # Focus and Scope - Journal's Focus and Scope, displayed on the Submissions page.
            ("general", "focus_and_scope", VALUE),
            #
            # From Address - System emails are sent From this address.
            ("general", "from_address", VALUE),
            #
            # Hide Author Email Links - If enabled the article page will not display links to email correspondence authors.
            ("article", "hide_author_email_links", VALUE),
            #
            # HTML Block Content - This is a homepage element that renders an HTML block
            ("plugin:HTML", "html_block_content", VALUE),
            #
            # Journal Uses HTTPS - Used for URL generation.
            ("general", "is_secure", VALUE),
            #
            # Journal Base Theme - When using a custom theme you can set the base theme, when a template from a custom theme is missing templates from the base theme will be used as a backup.
            ("general", "journal_base_theme", VALUE),
            #
            # Journal Description - Localised description of the journal.
            ("general", "journal_description", VALUE),
            #
            # Journal ISSN - The ISSN of the journal.
            ("general", "journal_issn", VALUE),
            #
            # Journal Languages - Languages available for this journal.
            ("general", "journal_languages", VALUE),
            #
            # Journal Name - Name of the journal.
            ("general", "journal_name", VALUE),
            #
            # Journal Theme - The HTML theme set to use for the journal.
            ("general", "journal_theme", VALUE),
            #
            # Enable the Keyword list page - Lists all of the keywords used by a journal and for each keyword a list of articles that use it.
            ("general", "keyword_list_page", VALUE),
            #
            # Display Login Page Notice - If set to true the Login Page Notice will display.
            ("general", "display_login_page_notice", VALUE),
            #
            # Main Contact - Primary contact for the journal.
            ("general", "main_contact", VALUE),
            #
            # Maintenance Mode Message - Message displayed when maintenance mode is enabled.
            ("general", "maintenance_message", VALUE),
            #
            # Enable Maintenance Mode - When enabled, non staff will not be able to access the site.
            ("general", "maintenance_mode", VALUE),
            #
            # Matomo Tracking Code - Tracking code for Matomo.
            ("general", "matromo_tracking_code", VALUE),
            #
            # News Title - Title for the News Page and Homepage block
            ("news", "news_title", VALUE),
            #
            # Number of Articles - Number of news articles to display on the homepage.
            ("plugin:News", "number_of_articles", VALUE),
            #
            # Number of Most Popular Articles to Display - Determines how many popular articles we should display.
            ("plugin:Popular Articles", "num_most_popular", VALUE),
            #
            # Password Reset - Email sent when user requests a password reset.
            ("email", "password_reset", VALUE),
            #
            # Journal Description for Press Site - Localised description of the journal specifically for the press' journal list page.
            ("general", "press_journal_description", VALUE),
            #
            # Print ISSN - The ISSN of the printed version of the journal.
            ("general", "print_issn", VALUE),
            #
            # External Privacy Policy URL - URL to an external privacy-policy, linked from the footer. If blank, it links to the Janeway CMS page: /site/privacy.
            ("general", "privacy_policy_url", VALUE),
            #
            # Publication Fees - Display of feeds for this journal. Displayed on the About and the Submission pages.
            ("general", "publication_fees", VALUE),
            #
            # Publisher Name - Name of the Journal's Publisher. Displayed throughout the site and metadata.
            ("general", "publisher_name", VALUE),
            #
            # Publisher URL - URL of the Journal's Publisher.
            ("general", "publisher_url", VALUE),
            #
            # Reader Publication Notification - Email sent readers when new articles are published.
            ("email", "reader_publication_notification", VALUE),
            #
            # Auto-register issue-level DOIs - Automatically register issue DOIs on article publication, based on the issue DOI pattern
            ("Identifiers", "register_issue_dois", VALUE),
            #
            # Reply-To Address - Address set as the 'Reply-to' for system emails.
            ("general", "replyto_address", VALUE),
            #
            # Send Reader Notifications - If enabled Janeway will notify readers of new published articles.
            ("notifications", "send_reader_notifications", VALUE),
            #
            # Password Reset - Subject for Email sent when user requests a password reset.
            ("email_subject", "subject_password_reset", VALUE),
            #
            # Subject Reader Publication Notification - Subject for Submission Access Request Complete.
            ("email_subject", "subject_reader_publication_notification", VALUE),
            #
            # User Email Change - Subject for Sent when an existing user updates their email address.
            ("email_subject", "subject_user_email_change", VALUE),
            #
            # Submission Checklist - Displayed on the About and Submission pages. You should update this with an ordered list of submission requirements.
            ("general", "submission_checklist", VALUE),
            #
            # Email message that is sent when an anonymous user subscribes to newsletters. - Message email body
            ("email", "subscribe_custom_email_message", VALUE),
            #
            # Janeway Support Contact for Staff - Support message to display to editors and staff on Manager page.
            ("general", "support_contact_message_for_staff", VALUE),
            #
            # Support Email - Support email address for editors and staff users.
            ("general", "support_email", VALUE),
            #
            # Suppress Citation Metrics - If enabled this will suppress the citations counter on the article page. The citation block will only appear for articles that have a citation. This setting is overruled by the Disable Metrics setting.
            ("article", "suppress_citations_metric", VALUE),
            #
            # Suppress How to Cite - If enabled this will suppress the how to cite block on the article page.
            ("article", "suppress_how_to_cite", VALUE),
            #
            # Switch Language - Allow users to change their language.
            ("general", "switch_language", VALUE),
            #
            # Twitter Handle - Journal's twitter handle.
            ("general", "twitter_handle", VALUE),
            #
            # Use Crossref DOIs - Whether or not to use Crossref DOIs.
            ("Identifiers", "use_crossref", VALUE),
            #
            # Use Google Analytics 4 - Use cookieless GA 4 instead of traditional analytics.
            ("general", "use_ga_four", VALUE),
            #
            # User Email Change - Subject for Sent when an existing user updates their email address.
            ("email_subject", "subject_user_email_change", VALUE),
        ]

        for group_name, setting_name, value in jcom_settings:
            setting_handler.save_setting(group_name, setting_name, jcom, VALUE)

    def add_arguments(self, parser):
        """Add arguments to command."""
        parser.add_argument(
            "--check-only",
            help="Just report the situation: do not set anything.",
        )
        parser.add_argument(
            "--force",
            help="Set all. By default, we don't change anything that is different from the default/unset state",
        )
