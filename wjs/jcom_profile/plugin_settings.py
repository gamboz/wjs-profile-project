from core.models import HomepageElement
from django.contrib.contenttypes.models import ContentType
from journal.models import Journal
from utils import plugins

PLUGIN_NAME = "WJS Plugin"
DISPLAY_NAME = "WJS Plugin"
DESCRIPTION = "A plugin to handle WJS HomePage elements"
AUTHOR = "Nephila"
VERSION = "0.1"
JANEWAY_VERSION = "1.3.9"  # the minimum version of Janeway that this plugin works with


class WjsPlugin(plugins.Plugin):
    plugin_name = PLUGIN_NAME
    display_name = DISPLAY_NAME
    description = DESCRIPTION
    author = AUTHOR
    version = VERSION
    janeway_version = JANEWAY_VERSION


def install():
    WjsPlugin.install()
    journal = Journal.objects.first()
    content_type = ContentType.objects.get_for_model(journal)
    HomepageElement.objects.create(
        name=PLUGIN_NAME,
        template_path="homepage_elements/latest_articles.html",
        content_type=content_type,
        object_id=journal.pk,
        has_config=False,
    )
    HomepageElement.objects.create(
        name=PLUGIN_NAME,
        template_path="homepage_elements/news.html",
        content_type=content_type,
        object_id=journal.pk,
        has_config=False,
    )
    HomepageElement.objects.create(
        name=PLUGIN_NAME,
        template_path="homepage_elements/newsletter_subscription.html",
        content_type=content_type,
        object_id=journal.pk,
        has_config=False,
    )


# Plugins can register for hooks, when a hook is rendered in a template the registered function will be called.
def hook_registry():
    return {
        "latest_articles_context": {
            "module": "wjs.jcom_profile.hooks",
            "function": "latest_articles_context",
            "name": PLUGIN_NAME,
        },
        "latest_news_context": {
            "module": "wjs.jcom_profile.hooks",
            "function": "latest_news_context",
            "name": PLUGIN_NAME,
        },
    }
