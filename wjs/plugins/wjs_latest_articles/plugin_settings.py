from pathlib import Path

from core.models import HomepageElement
from django.contrib.contenttypes.models import ContentType
from journal.models import Journal
from submission.models import Article
from utils import plugins

PLUGIN_NAME = "WJS Latest articles"
DISPLAY_NAME = "WJS Latest articles"
DESCRIPTION = "A plugin to provide latest articles home page element"
AUTHOR = "Nephila"
VERSION = "0.1"
SHORT_NAME = str(Path(__file__).parent)
JANEWAY_VERSION = "1.4.3"


class WJSLatestArticles(plugins.Plugin):
    short_name = SHORT_NAME
    plugin_name = PLUGIN_NAME
    display_name = DISPLAY_NAME
    description = DESCRIPTION
    author = AUTHOR
    version = VERSION
    janeway_version = JANEWAY_VERSION
    is_workflow_plugin = False


def install():
    WJSLatestArticles.install()
    journal = Journal.objects.first()
    content_type = ContentType.objects.get_for_model(journal)
    HomepageElement.objects.get_or_create(
        name=PLUGIN_NAME,
        defaults=dict(
            template_path="homepage_elements/latest_articles.html",
            content_type=content_type,
            object_id=journal.pk,
            has_config=False,
        )
    )


def hook_registry():
    return {
        "yield_homepage_element_context": {
            "module": f"plugins.{SHORT_NAME}.plugin_settings",
            "function": "latest_articles_context",
            "name": "JCOM Homepage",
        },

    }


def latest_articles_context(request, homepage_elements):
    return {
        "latest_articles": Article.objects.order_by("-date_published")[:10],
    }
