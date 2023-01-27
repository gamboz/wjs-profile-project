"""Process any SCSS and copy the resulting files into the main static folder.

Or just pass if not required. See
path/to/janeway/src/themes/OLH/build_assets.py as an example.

https://janeway.readthedocs.io/en/latest/configuration.html#theming

"""

import os

import sass
from django.conf import settings
from django.core.management import call_command

BASE_THEME_DIR = os.path.join(settings.BASE_DIR, "static", "JCOM-theme")
THEME_CSS_FILE = os.path.join(BASE_THEME_DIR, "css", "jcom.css")


def process_scss():
    """Compiles SCSS into CSS in the Static Assets folder."""
    app_scss_file = os.path.join(
        os.path.dirname(__file__),
        "assets",
        "sass",
        "jcom.scss",
    )
    compiled_css_from_file = sass.compile(filename=app_scss_file)

    # Open the CSS file and write into it
    with open(THEME_CSS_FILE, "w", encoding="utf-8") as write_file:
        write_file.write(compiled_css_from_file)


def create_paths():
    """Create destination dirs for css & co."""
    folders = [
        "css",
        # "js",
    ]

    for folder in folders:
        os.makedirs(os.path.join(BASE_THEME_DIR, folder), exist_ok=True)
    return os.path.join(BASE_THEME_DIR, "css")


def build():
    """Build assets and copy them to static folder."""
    override_css_dir = create_paths()
    process_scss()
    call_command("collectstatic", "--noinput")
