"""JCOM profile - Janeway's plugin configuration."""

from utils import plugins

PLUGIN_NAME = 'JCOM user profile'
DISPLAY_NAME = 'JCOM profile'
DESCRIPTION = 'Enrich default Janeway account with fields related to JCOM'
AUTHOR = 'Matteo'
VERSION = '0.1'
SHORT_NAME = 'wjs_jcom_profile'
MANAGER_URL = 'wjs_jcom_profile_manager'
JANEWAY_VERSION = "1.4"


class Wjs_jcom_profilePlugin(plugins.Plugin):
    plugin_name = PLUGIN_NAME
    display_name = DISPLAY_NAME
    description = DESCRIPTION
    author = AUTHOR
    short_name = SHORT_NAME
    manager_url = MANAGER_URL

    version = VERSION
    janeway_version = JANEWAY_VERSION
    


def install():
    Wjs_jcom_profilePlugin.install()


def hook_registry():
    Wjs_jcom_profilePlugin.hook_registry()


def register_for_events():
    pass
