"""The model for a field "profession" for JCOM authors."""

from django.db import models
from core.models import Account
from core.models import AccountManager
# TODO: use settings.AUTH_USER_MODEL
# from django.conf import settings

PROFESSIONS = (
    (0, 'A researcher in S&T studies,'
     ' science communication or neighbouring field'),
    (1, 'A practitioner in S&T'
     ' (e.g. journalist, museum staff, writer, ...)'),
    (2, 'An active scientist'),
    (3, 'Other'),
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
    profession = models.IntegerField(
        null=True,
        choices=PROFESSIONS)
