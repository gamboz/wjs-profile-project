"""Utility functions used only during data import."""
import requests
from core.models import Account, Country
from django.conf import settings
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
