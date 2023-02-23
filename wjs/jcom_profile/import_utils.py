"""Utility functions used only during data import."""
import re
from collections import namedtuple

import pycountry
import requests
from core.models import Account, Country
from django.conf import settings
from submission import models as submission_models
from utils.logger import get_logger

logger = get_logger(__name__)


# Janeway and wjapp country names do not completely overlap (sigh...)
COUNTRIES_MAPPING = {
    "Netherlands (the)": "Netherlands",
    "Philippines (the)": "Philippines",
    "Russian Federation (the)": "Russian Federation",
    "United Kingdom of Great Britain and Northern Ireland (the)": "United Kingdom",
    "United States of America (the)": "United States",
    "Taiwan": "Taiwan, Province of China",
}

JANEWAY_LANGUAGES_BY_CODE = {t[0]: t[1] for t in submission_models.LANGUAGE_CHOICES}
assert len(JANEWAY_LANGUAGES_BY_CODE) == len(submission_models.LANGUAGE_CHOICES)


FakeRequest = namedtuple("FakeRequest", ["user"])
# TODO: who whould this user be???
admin = Account.objects.filter(is_admin=True).first()
fake_request = FakeRequest(user=admin)


def query_wjapp_by_pubid(pubid, url="https://jcom.sissa.it/jcom/services/jsonpublished"):
    """Get data from wjapp."""
    apikey = settings.WJAPP_JCOM_APIKEY
    params = {
        "pubId": pubid,
        "apiKey": apikey,
    }
    response = requests.get(url=url, params=params)
    if response.status_code != 200:
        logger.warning(
            "Got HTTP code %s from wjapp for %s",
            response.status_code,
            pubid,
        )
        return {}
    return response.json()


def set_author_country(author: Account, json_data):
    """Set the author's country according to wjapp info."""
    country_name = json_data["countryName"]
    if country_name is None:
        logger.warning("No country for %s", json_data["userCod"])
        return
    country_name = COUNTRIES_MAPPING.get(country_name, country_name)
    try:
        country = Country.objects.get(name=country_name)
    except Country.DoesNotExist:
        logger.error("""Unknown country "%s" for %s""", country_name, json_data["userCod"])
    author.country = country
    author.save()


def drop_existing_galleys(article):
    """Clean up all existing galleys of an article."""
    for galley in article.galley_set.all():
        for file_obj in galley.images.all():
            file_obj.delete()
        galley.images.clear()
        galley.file.delete()
        galley.file = None
        galley.delete()
    article.galley_set.clear()
    article.render_galley = None
    article.save()


def decide_galley_label(pubid, file_name: str, file_mimetype: str):
    """Decide the galley's label."""
    # Remember that we can have ( PDF + EPUB galley ) x languages (usually two),
    # so a label of just "PDF" might not be sufficient.
    lang_match = re.search(r"_([a-z]{2,3})\.", file_name)
    mime_to_extension = {
        "application/pdf": "PDF",
        "application/epub+zip": "EPUB",
    }
    label = mime_to_extension.get(file_mimetype, None)
    if label is None:
        logger.error("""Unknown mime type "%s" for %s""", file_mimetype, pubid)
        label = "Other"
    language = None
    if lang_match is not None:
        language = lang_match.group(1)
        label = f"{label} ({language})"
    return (label, language)


def set_language(article, language):
    """Set the article's language.

    Must map from Drupal's iso639-2 (two chars) to Janeway iso639-3 (three chars).
    """
    lang = pycountry.languages.get(alpha_2=language)
    if lang.alpha_3 not in JANEWAY_LANGUAGES_BY_CODE:
        logger.error(
            'Unknown language "%s" (from "%s") for %s. Keeping default "English"',
            lang.alpha_3,
            language,
            article.get_identifier("pubid"),
        )
        return

    article.language = JANEWAY_LANGUAGES_BY_CODE[lang.alpha_3]
    if lang.name not in JANEWAY_LANGUAGES_BY_CODE.values():
        logger.warning(
            """ISO639 language for "%s" is "%s" and is different from Janeway's "%s" (using the latter) for %s""",
            language,
            lang.name,
            JANEWAY_LANGUAGES_BY_CODE[lang.alpha_3],
            article.get_identifier("pubid"),
        )
    article.save()


def publish_article(article):
    """Publish an article."""
    # see src/journal/views.py:1078
    article.stage = submission_models.STAGE_PUBLISHED
    article.snapshot_authors()
    article.close_core_workflow_objects()
    if article.date_published < article.issue.date_published:
        article.issue.date = article.date_published
        article.issue.save()
    article.save()
    logger.debug(f"Article {article.get_identifier('pubid')} run through Janeway's publication process")
