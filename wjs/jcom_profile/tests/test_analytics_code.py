"""Test that the analytics code set via the appropriate setting appears in some important pages."""
import faker
import pytest
from django.urls import reverse
from utils import setting_handler


def list_of_target_pages(article):
    """Build a list of important pages to check."""
    pages = (
        # Published article's landing page
        reverse("article_view", kwargs={"identifier_type": "pubid", "identifier": article.get_identifier("pubid")}),
        # Issues and volumes
        # All publications
        # Filter by keyword
    )
    return pages


@pytest.mark.django_db
def test_analytics_code(published_articles, generic_analytics_code_setting, client):
    """Set a random code and test that it's present in some important pages."""
    article = published_articles[0]
    random_text = faker.Faker().text()
    setting_handler.save_setting(
        "general",
        "analytics_code",
        article.journal,
        random_text,
    )
    for page in list_of_target_pages(article):
        response = client.get(page)
        assert response.status_code == 200
        response_text = response.content.decode()
        assert random_text in response_text
