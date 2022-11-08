"""The model for a field "profession" for JCOM authors."""
from core.models import Account, AccountManager, File
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from journal.models import Journal
from submission.models import Article
from utils import logic as utils_logic

# TODO: use settings.AUTH_USER_MODEL

PROFESSIONS = (
    (
        0,
        "A researcher in S&T studies," " science communication or neighbouring field",
    ),
    (
        1,
        "A practitioner in S&T" " (e.g. journalist, museum staff, writer, ...)",
    ),
    (2, "An active scientist"),
    (3, "Other"),
)


class JCOMProfile(Account):
    """An enrichment of Janeway's Account."""

    objects = AccountManager()
    # The following is redundant.
    # If not explicitly given, django creates a OTOField
    # named account_id_ptr.
    # But then I'm not sure how I should link the two:
    # see signals.py
    janeway_account = models.OneToOneField(
        Account,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    # Even if EO wants "profession" to be mandatory, we cannot set it
    # to `null=False` (i.e. `NOT NULL` at DB level) because we do not
    # have this data for most of our existing users.
    profession = models.IntegerField(null=True, choices=PROFESSIONS)
    gdpr_checkbox = models.BooleanField(_("GDPR acceptance checkbox"), default=False)
    invitation_token = models.CharField(_("Invitation token"), max_length=500, default="")


class Correspondence(models.Model):
    """Storage area for wjapp, PoS, SGP,... userCods."""

    # TODO: drop pk and use the three fields as pk

    account = models.ForeignKey(to=Account, on_delete=models.CASCADE, related_name="usercods")
    user_cod = models.PositiveIntegerField()
    sources = (
        ("jhep", "jhep"),
        ("pos", "pos"),
        ("jcap", "jcap"),
        ("jstat", "jstat"),
        ("jinst", "jinst"),
        ("jcom", "jcom"),
        ("jcomal", "jcomal"),
        ("sgp", "sgp"),
    )
    source = models.CharField(max_length=6, choices=sources)
    notes = JSONField(blank=True, null=True, encoder=DjangoJSONEncoder)
    email = models.EmailField(blank=True, null=True)
    orcid = models.CharField(max_length=40, null=True, blank=True)
    used = models.BooleanField(blank=True, null=False, default=False)

    class Meta:
        """Model's Meta."""

        unique_together = ("account", "user_cod", "source")


class SIQuerySet(models.QuerySet):
    def open_for_submission(self):
        """Build a queryset of Special Issues open for submission."""
        _now = timezone.now()
        return self.filter(open_date__lte=_now, close_date__gte=_now)

    def current_journal(self):
        """Build a queryset of all Special Issues of the "requested" journal."""
        request = utils_logic.get_current_request()
        if request and request.journal:
            return self.filter(journal=request.journal)
        else:
            return self.none()


class SpecialIssue(models.Model):
    """Stub for a special issue data model."""

    objects = SIQuerySet().as_manager()

    name = models.CharField(max_length=121, help_text="Name / title / long name", blank=False, null=False)
    short_name = models.SlugField(
        max_length=21,
        help_text="Short name or code (please only [a-zA-Z0-9_-]",
        blank=False,
        null=False,
    )
    description = models.TextField(help_text="Description or abstract", blank=False, null=False)

    # The real "nature" of the documents field would be a one-to-many
    # relationship from the File to the SI (i.e. each SI can have many
    # Files, but each File goes into one SI only), but File is
    # generic, so we fallback to to a many-to-many relationship
    documents = models.ManyToManyField(
        File,
        blank=True,
        null=True,
        help_text="By default, these files are internal use, but they can be published (i.e. shown onthe s.i. pages)"
        ' if the "galley" flag is set on the single file',
        # through=
        # --limit_choices_to=...--
    )

    open_date = models.DateTimeField(
        help_text="Authors can submit to this special issue only after this date",
        blank=True,
        null=False,
        default=timezone.now,
    )
    close_date = models.DateTimeField(
        help_text="Authors cannot submit to this special issue after this date",
        blank=True,
        null=True,
    )
    journal = models.ForeignKey(to=Journal, on_delete=models.CASCADE)

    def is_open_for_submission(self):
        """Compute if this special issue is open for submission."""
        # WARNING: must be coherent with queryset SIQuerySet
        now = timezone.now()
        return self.open_date <= now and self.close_date >= now

    def __str__(self):
        """Show representation (used in admin UI)."""
        if self.is_open_for_submission:
            return self.name
        else:
            return f"{self.name} - closed"


# class ArticleWrapper(Article):
class ArticleWrapper(models.Model):
    """An enrichment of Janeway's Article."""

    # Do not inherit from Article, otherwise we get Article's method
    # `save()` which does things that raise IntegrityError when called
    # from here...
    janeway_article = models.OneToOneField(
        Article,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
    )
    special_issue = models.ForeignKey(
        to=SpecialIssue,
        on_delete=models.DO_NOTHING,  # TODO: check me!
        related_name="special_issue",
        null=True,
    )
