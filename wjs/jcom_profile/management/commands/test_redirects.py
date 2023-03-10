"""Test (apache) redirects."""
import re

import requests
from django.core.management.base import BaseCommand
from utils.logger import get_logger

logger = get_logger(__name__)

TESTS = (
    # Landing page
    ("/archive/21/07/JCOM_2107_2022_A02", 301, "/article/pubid/JCOM_2107_2022_A02"),
    ("/archive/21/07/JCOM_2107_2022_A02/", 301, "/article/pubid/JCOM_2107_2022_A02/"),
    ("/archive/21/07/JCOM_2107_2022_A02/ciao", 301, "/article/pubid/JCOM_2107_2022_A02/ciao"),
    #     - old-style pubid
    ("/archive/01/01/E0101", 301, "/article/pubid/E0101"),
    # warning: remember that the last item is a regexp: () have special meaning
    ("/archive/09/04/Jcom0904(2010)E", 301, r"/article/pubid/Jcom0904\(2010\)E"),
    #
    # Issue
    ("/archive/03/03", 301, r"/issue/(\d+)/info"),
    ("/archive/03/03/", 301, r"/issue/(\d+)/info/"),
    #
    # Galleys
    ("/sites/default/files/documents/JCOM_2107_2022_A02.pdf", 301, r"/article/(\d+)/galley/(\d+)/download/"),
    ("/sites/default/files/documents/Jcom0904(2010)E_it.pdf", 301, r"/article/(\d+)/galley/(\d+)/download/"),
    #     - with language
    ("/sites/default/files/documents/JCOM_2002_2021_A01_en.pdf", 301, r"/article/(\d+)/galley/(\d+)/download/"),
    ("/sites/default/files/documents/JCOM_2002_2021_A01_pt.epub", 301, r"/article/(\d+)/galley/(\d+)/download/"),
    #     - citation_pdf_url (for google scholar, must be sibling or the paper's landing page)
    ("/archive/20/02/JCOM_2002_2021_A01_en.pdf", 301, r"/article/(\d+)/galley/(\d+)/download/"),
    ("/archive/22/01/JCOM_2201_2023_N01.pdf", 301, r"/article/(\d+)/galley/(\d+)/download/"),
)


class Command(BaseCommand):
    help = "Test (apache) redirects."  # noqa

    def handle(self, *args, **options):
        """Command entry point."""
        for request_path, expected_http_code, expected_location_path in TESTS:
            scheme_and_domain = f'{options["proto"]}://{options["domain"]}'
            url = f"{scheme_and_domain}{request_path}"
            response = requests.get(
                url=url,
                verify=options["ssl_no_verify"],
                allow_redirects=False,
            )

            if response.status_code != expected_http_code:
                self.error(f'got {response.status_code} (vs {expected_http_code}) for "{url}"')

            else:
                if expected_http_code in [301, 302]:
                    location_path = response.headers["Location"].replace(scheme_and_domain, "")
                    if match_obj := re.search(expected_location_path, location_path):
                        self.notice(f'"{url}" ok')
                        logger.debug(f"Match obj: {match_obj}")
                    else:
                        self.error(f"Got {location_path} (vs {expected_location_path}) for {url}")
                else:
                    self.error("WRITEME")

    def notice(self, msg):
        """Emit a notice."""
        self.stdout.write(self.style.NOTICE(msg))

    def error(self, msg):
        """Emit an error."""
        self.stdout.write(self.style.ERROR(msg))

    def add_arguments(self, parser):
        """Add arguments to command."""
        parser.add_argument(
            "--domain",
            default="jcom.sissa.it",
            help="The domain to test. Defaults to %(default)s.",
        )
        parser.add_argument(
            "--proto",
            default="https",
            help="Protocol / scheme of the request. Defaults to %(default)s.",
        )
        parser.add_argument(
            "--ssl-no-verify",
            action="store_false",
            help="Do not verify TLS certificate.",
        )
