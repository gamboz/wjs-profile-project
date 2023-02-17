"""Test the generation of the how-to-cite string."""

from collections import namedtuple

import pytest

from wjs.jcom_profile.templatetags.wjs_tags import how_to_cite
from wjs.jcom_profile.utils import abbreviate_first_middle, from_pubid_to_eid

MockAuthor = namedtuple(
    "MockAuthor",
    [
        "first_name",
        "middle_name",
        "last_name",
        "is_corporate",
        "corporate_name",
    ],
)


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
        "first,middle,last,is_corporate,corporate_name,sep,abbreviation",
        (
            ("Mario", "", "Rossi", False, None, "", "M."),
            # JCOM_2201_2023_A05
            ("Anne-Caroline", "", "Prévot", False, None, "", "A.-C."),
            # From PoS
            ("D'ann", "", "Barker", False, None, "", "D."),
            ("Haidar Mas'ud", "", "Alfanda", False, None, "", "H.M."),
            ("Natal'ya", "", "Peresadko", False, None, "", "N."),
            ("Re'em", "", "Sari", False, None, "", "R."),
            ("Shadi Adel Moh'd", "", "Bedoor", False, None, "", "S.A.M."),
            # With space as separator
            ("Anne-Caroline", "", "Prévot", False, None, " ", "A.-C."),
            ("D'ann", "", "Barker", False, None, " ", "D."),
            ("Shadi Adel Moh'd", "", "Bedoor", False, None, " ", "S. A. M."),
            # Corporate - expect no abbreviation
            ("First", "Middle", "Last", True, "Corporate name", "", "Corporate name"),
            # With middlename (from PoS) - no space
            ("C.-J.", "David", "Lin", False, None, "", "C.-J.D."),
            ("Kim-Vy", "H.", "Tran", False, None, "", "K.-V.H."),
            ("M.-H.", "A.", "Huang", False, None, "", "M.-H.A."),
            ("Niels-Uwe", "Friedrich", "Bastian", False, None, "", "N.-U.F."),
            ("Zh.-A.", "M.", "Dzhilkibaev", False, None, "", "Z.-A.M."),
            ("Zhan-Arys", "Magysovich", "Dzhilkibaev", False, None, "", "Z.-A.M."),
            ("Zhan-Arys", "M.", "Dzhlkibaev", False, None, "", "Z.-A.M."),
            # With middlename (from PoS) - with space
            ("C.-J.", "David", "Lin", False, None, " ", "C.-J. D."),
            ("Kim-Vy", "H.", "Tran", False, None, " ", "K.-V. H."),
            ("M.-H.", "A.", "Huang", False, None, " ", "M.-H. A."),
            ("Niels-Uwe", "Friedrich", "Bastian", False, None, " ", "N.-U. F."),
            ("Zh.-A.", "M.", "Dzhilkibaev", False, None, " ", "Z.-A. M."),
            ("Zhan-Arys", "Magysovich", "Dzhilkibaev", False, None, " ", "Z.-A. M."),
            ("Zhan-Arys", "M.", "Dzhlkibaev", False, None, " ", "Z.-A. M."),
        ),
    )
    def test_abbreviate_first_middle(
        self,
        first,
        middle,
        last,
        is_corporate,
        corporate_name,
        sep,
        abbreviation,
    ):
        """Test the abbreviation of given names."""
        author = MockAuthor(first, middle, last, is_corporate, corporate_name)
        assert abbreviate_first_middle(author, sep=sep) == abbreviation


class TestHTC:
    """Test How To Cite."""

    def test_htc(self):
        """Test that the how-to-cite template filter produces the expected string."""
        assert not how_to_cite(None)
