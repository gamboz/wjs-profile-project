"""Default configuration for Janeway's plugin."""

from utils import models

PLUGIN_NAME = 'JCOM user profile'
DESCRIPTION = """Enrich Janeway's user profile with a field "profession"."""
AUTHOR = 'mg'
VERSION = '1.0'
SHORT_NAME = 'wjs_jcom_profile'
# MANAGER_URL = 'books_admin'
JANEWAY_VERSION = "1.4"


def install():
    """TODO: what should I do here?."""
    new_plugin, created = models.Plugin.objects.get_or_create(
        name=SHORT_NAME,
        enabled=True,
        # This should be "False", because the enriched profile is
        # useful only for JCOM, but the DB tables and URL routing are
        # general. So I'm keeping it "True".
        press_wide=True,
        defaults={'version': VERSION},
    )

    if created:
        print('Plugin {0} installed.'.format(PLUGIN_NAME))
    else:
        print('Plugin {0} is already installed.'.format(PLUGIN_NAME))


def hook_registry():
    """TODO: what should I do here?."""
    pass
