import re

import pytest
from core.models import File
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from identifiers.models import Identifier
from utils.testing.helpers import create_galley


@pytest.mark.django_db
def test_redirect_issues_from_jcom_to_janeway_url(issue):
    client = Client()
    url = reverse("jcom_redirect_issue", kwargs={"volume": "1", "issue": issue.issue})
    expected_redirect_url = reverse(
        "journal_issue",
        kwargs={
            "issue_id": issue.pk,
        },
    )
    response = client.get(url, follow=True)
    actual_redirect_url, status_code = response.redirect_chain[-1]

    assert status_code == 302
    assert expected_redirect_url == actual_redirect_url


@pytest.fixture
def published_article_with_standard_galleys(admin, article_journal, sections, keywords, article_factory):
    """Create articles in published stage with PDF and EPUB galleys."""
    # TODO: replace me with fb_article
    article = article_factory(
        journal=article_journal,
        date_published=timezone.now(),
        stage="Published",
    )
    Identifier.objects.create(
        id_type="pubid",
        article=article,
        identifier="JCOM_0102_2023_A04",
    )
    for extension in ["pdf", "epub"]:
        file_obj = File.objects.create(
            # TODO: we could use the original_filename to match the
            # requested galley, but first we must verify if the
            # original file name always appears in the link (check
            # simple galleys, original language vs. translations and
            # any combination of these with the manual errors _0
            # _1...) and verify if during import we collect and store
            # the original file name in the galley.
            original_filename=f"Anything.{extension}",
        )
        galley = create_galley(article, file_obj)
        galley.article = article
        galley.last_modified = timezone.now()
        galley.label = extension.upper()  # ⇦ important! The label is used to find the correct galley
        galley.save()
    return article


def url_to_label(url):
    """Return the expected galley label that one would expect from the give url."""
    pattern = re.compile(r"(?P<pubid>[\w.()-]+)(?P<error>_\d)?(?P<language>_\w{2})?\.(?P<extension>pdf|epub)$")
    if match := re.search(pattern, url):
        label = match.group("extension").upper()
        if language := match.group("language"):
            label = f"{label} ({language})"
        return label
    return None


@pytest.mark.django_db
def test_redirect_galley_from_jcom_to_janeway_url(issue, published_article_with_standard_galleys):
    """Test redirect of simples galley/attachments/files from Drupal style."""
    article = published_article_with_standard_galleys
    pubid = article.get_identifier(identifier_type="pubid")
    pesky_urls = [
        f"sites/default/files/documents/{pubid}.pdf",
        # TODO: f"sites/default/files/documents/{pubid}_en.pdf",
        # TODO: f"sites/default/files/documents/{pubid}_0.pdf",
        # TODO: f"sites/default/files/documents/{pubid}_pt_01.pdf",
        #
        f"sites/default/files/documents/{pubid}.epub",
        # TODO: f"sites/default/files/documents/{pubid}_en.epub",
        # TODO: f"sites/default/files/documents/{pubid}_0.epub",
        # TODO: f"sites/default/files/documents/{pubid}_pt_01.epub",
    ]
    client = Client()
    for pesky_url in pesky_urls:
        url = f"/{article.journal.code}/{pesky_url}"
        response = client.get(url, follow=True)
        actual_redirect_url, status_code = response.redirect_chain[-1]
        assert status_code == 302
        label = url_to_label(url)
        galley = article.galley_set.get(label=label)
        expected_redirect_url = reverse(
            "article_download_galley",
            kwargs={
                "article_id": galley.article.pk,
                "galley_id": galley.pk,
            },
        )
        assert expected_redirect_url == actual_redirect_url


@pytest.mark.django_db
def test_redirect_nonexistent_galley_from_jcom_to_janeway_url(article_journal):
    client = Client()
    url = reverse("jcom_redirect_file", kwargs={"pubid": "nonexisting", "extension": "pdf"})
    response = client.get(url, follow=True)
    assert response.status_code == 404
