"""Tests (first attempt)."""

import pytest
from django.test import TestCase
from core.models import Account
from django.core.exceptions import ObjectDoesNotExist
from wjs.jcom_profile.models import JCOMProfile
# from utils.testing import helpers


class JCOMProfileProfessionModelTests(TestCase):

    def setUp(self):
        """Do setup."""
        self.username = 'userX'
        self.drop_userX()

    # TODO: check
    # https://docs.djangoproject.com/en/4.0/topics/testing/overview/#rollback-emulation
    def drop_userX(self):
        """
        Remove "userX".

        Because I'm expecting to re-use the same DB for multiple
        tests.
        """
        try:
            userX = Account.objects.get(username=self.username)
        except ObjectDoesNotExist:
            pass
        else:
            userX.delete()

    def test_new_account_has_profession_but_it_is_not_set(self):
        """A newly created account must have a profession associated.

        However, the profession is not set by default.
        """
        self.drop_userX()
        userX = Account(username=self.username,
                        first_name="User", last_name="Ics")
        userX.save()
        again = Account.objects.get(username=self.username)
        self.assertEqual(again.username, self.username)
        self.assertIsNone(again.jcomprofile.profession)

    def test_account_can_save_profession(self):
        """One can set and save a profession onto an account."""
        self.drop_userX()
        userX = Account(username=self.username,
                        first_name="User", last_name="Ics")
        userX.save()

        # Not sure if it would be cleaner to
        #    from .models import PROFESSIONS
        #    profession = PROFESSIONS[random.randint(0, len(PROFESSIONS))]
        # (or something similar)
        # I think not...
        profession_id = 2
        jcom_profile = JCOMProfile(janeway_account=userX)
        jcom_profile.profession = profession_id
        jcom_profile.save()

        userX.accountprofession = jcom_profile
        userX.save()

        again = Account.objects.get(username=self.username)
        self.assertEqual(again.username, self.username)
        self.assertEqual(again.jcomprofile.profession, profession_id)


# TODO: test that django admin interface has an inline with the
# profile extension. Do I really care?

class JCOMProfileURLs(TestCase):

    def setUp(self):
        """Prepare a journal with "JCOM" graphical theme."""
        self.journal_code = 'PIPPO'
        self.create_journal()

    def create_journal(self):
        """Create a press/journal and set the graphical theme."""
        # copied from journal.tests.test_models
        from django.test.client import RequestFactory
        from journal.tests.utils import make_test_journal
        from press.models import Press
        self.request_factory = RequestFactory()
        self.press = Press(domain="sitetestpress.org")
        self.press.save()
        self.request_factory
        journal_kwargs = dict(
            code=self.journal_code,
            domain="sitetest.org",
            # journal_theme='JCOM',  # No!
        )
        self.journal = make_test_journal(**journal_kwargs)

    @pytest.mark.skip(reason="Package installed as app (not as plugin).")
    def test_registerURL_points_to_plugin(self):
        """The "register" link points to the plugin's registration form."""
        from django.test import Client
        client = Client()
        journal_path = f"/{self.journal_code}/"
        response = client.get(journal_path)
        expected_register_link = \
            f'/{self.journal_code}/plugins/register/step/1/"> Register'
        #                          ^^^^^^^
        # Attenzione allo spazio prima di "Register"!
        # In the case of an app, use the following:
        #    f'/{self.journal_code}/register/step/1/"> Register'
        #                          ^_ no "/plugins" path
        self.assertContains(response, expected_register_link)
