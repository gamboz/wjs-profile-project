"""Test the generation of the how-to-cite string."""

from collections import namedtuple

import pytest

from wjs.jcom_profile.templatetags.wjs_tags import how_to_cite
from wjs.jcom_profile.utils import abbreviate_first_middle, from_pubid_to_eid

MockAuthor = namedtuple("MockAuthor", ["first_name", "middle_name", "last_name", "is_corporate"])


class TestUtils:
    """Test unittest-friendly utility functions."""

    @pytest.mark.parametrize(
        "pubid,eid",
        (
            ("JCOM_1401_2015_C02", "C02"),
            ("JCOM_1401_2015_E", "E"),
            ("Jcom1102(2012)A01", "A01"),
            ("Jcom1102(2012)E", "E"),
            ("R020401", "R01"),
            ("E0204", "E"),
        ),
    )
    def test_from_pubid_to_eid(self, pubid, eid):
        """Test the extraction of the eid from the pubid."""
        assert from_pubid_to_eid(pubid) == eid

    @pytest.mark.parametrize(
        "author,abbreviation",
        (
            (
                MockAuthor(
                    first_name="Mario",
                    middle_name="",
                    last_name="Rossi",
                    is_corporate=False,
                ),
                "M.",
            ),
            # JCOM_2201_2023_A05
            (
                MockAuthor(
                    first_name="Anne-Caroline",
                    middle_name="",
                    last_name="Prévot",
                    is_corporate=False,
                ),
                "A.-C.",
            ),
            (
                MockAuthor(
                    first_name="D'ann",
                    middle_name="",
                    last_name="Barker",
                    is_corporate=False,
                ),
                "D.",
            ),
            (
                MockAuthor(
                    first_name="Haidar Mas'ud",
                    middle_name="",
                    last_name="Alfanda      ",
                    is_corporate=False,
                ),
                "H.M.",
            ),
            (
                MockAuthor(
                    first_name="Natal'ya",
                    middle_name="",
                    last_name="Peresadko",
                    is_corporate=False,
                ),
                "N.",
            ),
            (
                MockAuthor(
                    first_name="Re'em",
                    middle_name="",
                    last_name="Sari",
                    is_corporate=False,
                ),
                "R.",
            ),
            (
                MockAuthor(
                    first_name="Shadi Adel Moh'd",
                    middle_name="",
                    last_name="Bedoor",
                    is_corporate=False,
                ),
                "S.A.M.",
            ),
        ),
    )
    def test_abbreviate_first_middle(self, author, abbreviation):
        """Test the abbreviation of given names."""
        assert abbreviate_first_middle(author) == abbreviation
