"""Tests related to the submission process."""

import pytest
from core.models import Account, Role, Setting, SettingGroup, SettingValue
from django.test import Client
from submission import logic
from submission.models import Article
from django.core.cache import cache

class TestFilesStage:
    """Tests related to the file-submission stage."""

    @pytest.mark.django_db
    def test_additional_files_form_title_obeys_setting(self, journal):
        """The title of the additional files field should obey its setting."""
        # set the setting
        value = "<h2>Qui ci metto un po' <strong>di</strong> tutto</h2>"
        setting_group = SettingGroup.objects.get(name="styling")
        setting = Setting.objects.get(
            name="submission_figures_data_title", group=setting_group
        )
        setting_value, _ = SettingValue.objects.get_or_create(
            journal=journal, setting=setting
        )
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
