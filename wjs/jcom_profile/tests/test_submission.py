"""Tests related to the submission process."""
import lxml.html
import pytest
from core.middleware import SiteSettingsMiddleware
from core.models import Account, Role, Setting, SettingGroup, SettingValue
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.cache import cache
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from submission import logic
from submission.models import Article, Section

from wjs.jcom_profile import views
from wjs.jcom_profile.models import SpecialIssue


class TestFilesStage:
    """Tests related to the file-submission stage."""

    @pytest.mark.django_db
    def test_additional_files_form_title_obeys_setting(self, journal, clear_script_prefix_fix):
        """The title of the additional files field should obey its setting."""
        # TODO: flip-flapping when the order of the tests change!!!
        # set the setting
        value = "<h2>Qui ci metto un po' <strong>di</strong> tutto</h2>"
        setting_group = SettingGroup.objects.get(name="styling")
        setting = Setting.objects.get(name="submission_figures_data_title", group=setting_group)
        setting_value, _ = SettingValue.objects.get_or_create(journal=journal, setting=setting)
        setting_value.value = value
        setting_value.save()

        client = Client()

        user = Account.objects.get_or_create(username="testuser", email="a@b.c")[0]
        user.is_active = True
        user.jcomprofile.gdpr_checkbox = True
        user.jcomprofile.save()
        user.save()

        # start a submission
        article = Article.objects.create(
            journal=journal,
            title="A title",
            current_step=3,
            owner=user,
            correspondence_author=user,
        )
        # for the value of "step", see submission.models.Article::step_to_url
        # Magic here ⮧ (see utils/install/roles.json)
        Role.objects.create(name="Author", slug="author")
        logic.add_user_as_author(user=user, article=article)

        # visit the correct page
        client.force_login(user)
        url = f"{journal.code}/{article.step_to_url()}"
        response = client.get(url)
        # I'm expecting an "OK" response, not a redirect to /login or
        # /profile (e.g. for the gdpr checkbox)
        assert response.status_code == 200

        # check that the setting's value is there
        assert value in response.content.decode()

        # double check
        new_value = "ciao 🤞"
        setting_value.value = new_value
        setting_value.save()
        # django tests and cache; a bit unexpected:
        # https://til.codeinthehole.com/posts/django-doesnt-flush-caches-between-tests/
        cache.clear()  # 🠄 Important!
        response = client.get(url)
        assert new_value in response.content.decode()

    @pytest.mark.xfail
    @pytest.mark.django_db
    def test_admin_cannot_login(self, journal, admin):
        """Background study.

        Sembra che l'account admin (dalla fixture conftest.admin) non
        riesca ad autenticarsi...

        """
        client = Client()
        admin.jcomprofile.gdpr_checkbox = True
        admin.jcomprofile.save()
        client.force_login(admin)
        response = client.get("/")
        ru = response.wsgi_request.user
        assert ru is not None
        assert ru.is_authenticated


class TestSIStage:
    """Tests related to the "info" stage."""

    @pytest.mark.django_db
    def test_choose_si_skipped_when_no_si_exist(self, admin, article):
        """Test that the SI-choosing page just redirects if there are no SIs."""
        client = Client()
        client.force_login(admin)
        # visit the correct page
        url = reverse("submit_info", args=(article.pk,))
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == reverse("submit_info_original", args=(article.pk,))

    @pytest.mark.django_db
    def test_choose_si_skipped_when_no_open_si(self, admin, article):
        """Test that the SI-choosing page just redirects if there are
        SIs with open date in the future and no close date."""
        client = Client()
        client.force_login(admin)
        tomorrow = timezone.now() + timezone.timedelta(1)
        SpecialIssue.objects.create(name="Test SI", journal=article.journal, open_date=tomorrow)
        assert not SpecialIssue.objects.open_for_submission().exists()
        url = reverse("submit_info", args=(article.pk,))
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == reverse("submit_info_original", args=(article.pk,))

    @pytest.mark.django_db
    def test_choose_si_shown_when_si_open(self, admin, article):
        """Test that the SI-choosing page is shown if there are SIs
        with open date in the past and no close date."""
        client = Client()
        client.force_login(admin)
        yesterday = timezone.now() - timezone.timedelta(1)
        SpecialIssue.objects.create(name="Test SI", journal=article.journal, open_date=yesterday)
        assert SpecialIssue.objects.open_for_submission().exists()
        # visit the correct page
        url = reverse("submit_info", args=(article.pk,))
        response = client.get(url)

        assert response.status_code == 200
        targets = (
            "<h1>Submission Destination",
            "Choose Submission Destination",
        )
        content = response.content.decode()
        for target in targets:
            assert target in content

    @pytest.mark.django_db
    def test_choose_si_shown_when_si_open_and_not_yet_closed(self, admin, article):
        """Test that the SI-choosing page is shown if there are SIs
        with open date in the past and close date in the future."""
        client = Client()
        client.force_login(admin)
        yesterday = timezone.now() - timezone.timedelta(1)
        tomorrow = timezone.now() + timezone.timedelta(1)
        SpecialIssue.objects.create(name="Test SI", journal=article.journal, open_date=yesterday, close_date=tomorrow)
        assert SpecialIssue.objects.open_for_submission().exists()
        # visit the correct page
        url = reverse("submit_info", args=(article.pk,))
        response = client.get(url)

        assert response.status_code == 200
        targets = (
            "<h1>Submission Destination",
            "Choose Submission Destination",
        )
        content = response.content.decode()
        for target in targets:
            assert target in content


@pytest.fixture
def journal_with_three_sections(article_journal):
    """Set three sections to a journal.

    Two "public" (article and letter) and one not "public" (editorial).
    """
    # All journals automatically get a section, so there is no need to
    # Section.objects.create(name="Article",...
    Section.objects.create(name="Letter", sequence=10, journal=article_journal, public_submissions=True).save()
    Section.objects.create(name="Editorial", sequence=10, journal=article_journal, public_submissions=False).save()
    article_journal.save()
    return article_journal


@pytest.fixture
def special_issue_with_one_section(journal_with_three_sections):
    """Make a special issue with only one "section" named "article"."""
    sections = journal_with_three_sections.section_set.all()
    yesterday = timezone.now() - timezone.timedelta(1)
    special_issue = SpecialIssue.objects.create(
        journal=journal_with_three_sections,
        name="Special Issue One Section",
        description="SIONE description",
        short_name="SIONE",
        open_date=yesterday,
        allowed_sections=sections,
    )
    return special_issue


@pytest.fixture
def special_issue_with_two_sections(journal_with_three_sections):
    """Make a special issue with two "sections".

    One "public" (article) and one not "public" (editorial)."""
    sections = (
        Section.objects.get(name="Article", journal=journal_with_three_sections, public_submissions=True),
        Section.objects.get(name="Editorial", journal=journal_with_three_sections, public_submissions=False),
    )
    yesterday = timezone.now() - timezone.timedelta(1)
    special_issue = SpecialIssue.objects.create(
        journal=journal_with_three_sections,
        name="Special Issue Two Sections",
        description="SITWO description",
        short_name="SITWO",
        open_date=yesterday,
        allowed_sections=sections,
    )
    return special_issue


class TestInfoStage:
    """Test which section choices are presented to the author.

    Possibilities:
    - no SI has been choosen (normal submission)
      - if manager/editor: all sections
      - if not manager/editor: only "public" sections
    - SI has been choosen
      - SI allows all sections
        - same as "no SI"
      - SI allows subset of journal's sections
        - if manager/editor: all sections allowed by SI
        - if not manager/editor: only "public" sections allowed by SI
        - in any case: no section that is not allowed by the SI
    """

    @pytest.mark.django_db
    def test_no_si_choosen_manager_submitting(self, rf, admin, journal_with_three_sections):
        """When no SI has been choosen, a manager sees all sections."""
        # I had to import here because pytest complains about missing `django_db` mark otherwise
        from wjs.jcom_profile.management.commands.create_random_data import (
            ArticleFactory,
        )

        # create an article owned by the user that will do the request (admin)
        article = ArticleFactory.create(journal=journal_with_three_sections, owner=admin)

        url = reverse("submit_info", args=(article.pk,))
        request = rf.get(url)

        # simulate login
        request.user = admin
        # simulate session middleware (it is needed because the
        # template of the response uses the templatetag
        # "hijack_notification")
        SessionMiddleware().process_request(request)
        # simulate J. middleware
        request.journal = journal_with_three_sections
        SiteSettingsMiddleware.process_request(request)
        # https://youtu.be/vZraNnWnYXE?t=10

        response = views.submit_info(request, article_id=article.id)
        # NB: do NOT use unnamed args as in ...submit_info(request, article.id)!!!
        assert response.status_code == 200
        html = lxml.html.fromstring(response.content.decode())
        sections_select = html.get_element_by_id(id="id_section")
        sections_options = sections_select.findall("option")
        # expect three section + the empty label
        assert len(sections_options) == 4

        texts = [e.text for e in sections_options]
        values = [e.attrib.get("value") for e in sections_options]
        for section in journal_with_three_sections.section_set.all():
            assert str(section.id) in values
            section_text = str(section)
            assert section_text in texts

    @pytest.mark.skip
    @pytest.mark.django_db
    def test_no_si_choosen_author_submitting(self, coauthor, journal_with_three_sections):
        """When no SI has been choosen, a normal author (i.e. not manager) sees only public sections."""
        assert "TODO" == "DONE"
