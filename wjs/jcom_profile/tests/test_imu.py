"""Test Import Many Users functionality"""

import io

import pytest
from django.urls import reverse
from imu_bits import (
    FOGLIO1,
    FOGLIO2,
    FOGLIO3,
    FOGLIO4,
    FOGLIO5,
    expectations1,
    expectations2,
    expectations3,
    expectations4,
    expectations5,
)
from odf.opendocument import OpenDocumentSpreadsheet
from odf.table import Table, TableCell, TableRow
from odf.text import P


def make_ods(data):
    """Return a ods file with the give data.

    Data is a list of lists (rows/cols).
    """
    # Generate document object
    doc = OpenDocumentSpreadsheet()
    table = Table()

    def newtc(value):
        tc = TableCell(valuetype="string")
        tc.addElement(P(text=value))
        return tc

    for row in data:
        tr = TableRow()
        for col in row:
            tr.addElement(newtc(col))
            table.addElement(tr)

    # save ods
    doc.spreadsheet.addElement(table)
    f = io.BytesIO()
    doc.save(f, False)
    f.seek(0)
    return {
        "file": ("x.ods", f, "application/vnd.oasis.opendocument.spreadsheet"),
    }


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (make_ods(FOGLIO1), expectations1),
        (make_ods(FOGLIO2), expectations2),
        (make_ods(FOGLIO3), expectations3),
        (make_ods(FOGLIO4), expectations4),
        (make_ods(FOGLIO5), expectations5),
    ],
)
@pytest.mark.django_db
def test_admin_IMU_upload(
    test_input,
    expected,
    article_journal,
    client,
    admin,
    existing_user,
    special_issue,
):
    """Admin uploads ods file with authors."""
    client.force_login(admin)
    url = reverse("si-imu-1", kwargs={"pk": special_issue.id})
    data = dict(
        data_file=test_input,
        create_articles_on_import="on",
        match_euristic="optimistic",
        type_of_new_articles=special_issue.allowed_sections.first().id,
    )
    response = client.post(url, data)
    assert response.status_code == 200

    assert "write me!!!" in response.content.decode()


# 1 contribution ✕ 1 smilar - new
block_0 = dict(
    lastname_0="Gamboz",
    middlename_0=None,
    firstname_0="Matteo",
    affiliation_0="ml",
    email_0="gamboz@medialab.sissa.it",
    title_0="block 1 ᛒ",
    session_0="0",
    similar_0_0="12325",
    choosen_0="new",
    sessions="Main session",
    users=0,
)
expected_0 = [
    "<td>block 1 ᛒ</td>",
    '<td>new <a href="gest_users.cgi?action=UPD&amp;author=',
    "No user needs modification.",
]

# 1 contribution ✕ 1 smilar - db
block_1 = dict(
    lastname_0="Gamboz",
    middlename_0=None,
    firstname_0="Matteo",
    affiliation_0="ml",
    email_0="gamboz@medialab.sissa.it",
    title_0="block 2 ᛒ",
    session_0="0",
    similar_0_0="12325",
    choosen_0="db_0",
    sessions="Main session",
    users=0,
)
expected_1 = [
    "<td>block 2 ᛒ</td>",
    "<td>DB</td>",
    "No user needs modification.",
]

# 1 contribution ✕ 1 smilar - modify
block_2 = dict(
    lastname_0="Gamboz",
    middlename_0=None,
    firstname_0="Matteo",
    affiliation_0="〒 ml",
    email_0="gamboz@medialab.sissa.it",
    title_0="block 3 ᛒ",
    session_0="0",
    similar_0_0="12325",
    choosen_0="modify_0",
    sessions="Main session",
    users=0,
)
expected_2 = [
    "<td>block 3 ᛒ</td>",
    "<td>DB",
    '<td><input type="text" name="affiliation_12325"	value="〒 ml" /></td>',
]

# 2 contributions + first fails - db
block_3 = dict(
    lastname_0="Gamboz",
    middlename_0=None,
    firstname_0="Matteo",
    affiliation_0="〒 ml",
    email_0="gamboz@medialab.sissa.it",
    title_0="block 4 ᛒ",
    session_0="0",
    similar_0_0="12325",
    choosen_0="db_0",
    #
    lastname_1="Gamboz",
    middlename_1=None,
    firstname_1="Matteo",
    affiliation_1="〒 ml",
    email_1="gamboz@medialab.sissa.it",
    title_1="block 4 ᛒ",
    session_1="0",
    similar_1_0="12325",
    choosen_1="db_0",
    #
    sessions="Main session",
    users=1,
)
expected_3 = [
    "<td>block 4 ᛒ</td>",
    "<td>DB",
    "Contribution already present (same author, title, session).",
]

# 2 contributions from the same author, same email; both are checked "new"
block_4 = dict(
    lastname_0="Newone",
    middlename_0=None,
    firstname_0="User",
    affiliation_0="Xyz",
    email_0="newone@xyz.it",
    title_0="title ふう",
    session_0="0",
    choosen_0="new",
    #
    lastname_1="Newone",
    middlename_1=None,
    firstname_1="User",
    affiliation_1="Xyz",
    email_1="newone@xyz.it",
    title_1="title ばる",
    session_1="0",
    choosen_1="new",
    #
    sessions="Main session",
    users=1,
)
expected_4 = [
    # strings that should be relative to the _first_ record:
    "<td>title ふう</td>",
    "<td>new</td>",
    "inserted </td>",
    # strings that should be relative to the _second_ record:
    "<td>title ばる</td>",
    "<td>already inserted (see",
    "<td>DB</td>",
]

# Same as block_4, but the emails of the accounts are different
# case-wise. The expected behavior does not change.
block_5 = dict(
    lastname_0="Newone",
    middlename_0=None,
    firstname_0="User",
    affiliation_0="Xyz",
    email_0="newone@xyz.it",
    title_0="title ふう",
    session_0="0",
    choosen_0="new",
    #
    lastname_1="Newone",
    middlename_1=None,
    firstname_1="User",
    affiliation_1="Xyz",
    email_1="NEWONE@xyz.it",  # only difference with block_4
    title_1="title ばる",
    session_1="0",
    choosen_1="new",
    #
    sessions="Main session",
    users=1,
)
expected_5 = [
    # strings that should be relative to the _first_ record:
    "<td>title ふう</td>",
    "<td>new</td>",
    "inserted </td>",
    # strings that should be relative to the _second_ record:
    "<td>title ばる</td>",
    "<td>already inserted (see",
    "<td>DB</td>",
]

expected_generic = (
    "mailto:%(eo_mail_encoded)s",
    "<h1>Load multiple users</h1>",
)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (block_0, expected_0),
        (block_1, expected_1),
        (block_2, expected_2),
        (block_3, expected_3),
        (block_4, expected_4),
        (block_5, expected_5),
    ],
)
def donttest_administrator_IMU_check(
    test_input,
    expected,
    admin_auth,
    new_user,
    new_conference,
    new_contribution,
    sessionid_of_new_contribution,
    db_connection,
    check_output,
):
    """Admin inserts many users (phase 2 (check): ods uploaded and results presetend."""
    with db_connection.cursor() as cursor:
        cursor.execute(
            "select count(*) as contribs from conf where confid = %s",
            (new_conference,),
        )
        db_connection.commit()
        assert cursor.rowcount == 1
        record = cursor.fetchone()
        assert record["contribs"] == 1

    expected.extend(expected_generic)
    test_input.setdefault("confid", new_conference)
    check_output(
        url_path="/cgi-bin/administrator/insert_many_users_check.cgi",
        request_parameters=test_input,
        expected_output=tuple(expected),
        auth=admin_auth,
        request_method=Methods.POST,
    )

    # cleanup (so that other tests find standard condition)
    with db_connection.cursor() as cursor:
        cursor.execute(
            "delete from preproc where confid = %s and preid != %s",
            (new_conference, new_contribution),
        )
        db_connection.commit()
        # ugly... relies on knowledge of the test input
        cursor.execute("delete from user where email='gamboz@medialab.sissa.it' and uid != 12325")
        db_connection.commit()
