"""Test Import Many Users functionality"""

import io

import lxml.html
import pytest
from django.urls import reverse
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
    return f


@pytest.mark.django_db
def test_si_imu_upload_one_existing_one_new(
    article_journal,
    client,
    admin,
    existing_user,
    special_issue,
):
    """Upload a sheet with one-existing / one-new authors."""
    client.force_login(admin)
    url = reverse("si-imu-1", kwargs={"pk": special_issue.id})

    # foglio 1: "Main session" + 2 contributi diversi (diversi autori e
    # titolo). Il primo autore è già presente nel DB.
    foglio = (
        ("Main session", None, None, None, None, None),
        (
            existing_user.first_name,
            existing_user.middle_name,
            existing_user.last_name,
            existing_user.email,
            existing_user.institution,
            "Title ふう",
        ),
        ("Novicius", None, "Fabulator", "nfabulator@dmain.net", "Affilia", "Title ばる"),
    )
    ods = make_ods(foglio)
    data = dict(
        data_file=ods,
        create_articles_on_import="on",
        match_euristic="optimistic",
        type_of_new_articles=special_issue.allowed_sections.first().id,
    )
    response = client.post(url, data)

    # Preliminary checks
    assert response.status_code == 200
    expectations = (
        "Insert Users — Step 2/3",  # NB: second step! Looking at the POST
        'name="email_1" value="iamsum@example.com"',
        'name="email_2" value="nfabulator@dmain.net"',
        "Title ふう",
        "Title ばる",
    )
    response_content = response.content.decode()
    for expected in expectations:
        assert expected in response_content

    # Interesting checks
    html = lxml.html.fromstring(response_content)
    # Row 0 is for the "partition", we don't care.
    # Row 1 is about the already exising user: expect an "edit" action:
    a1 = html.find(".//input[@name='action-1'][@checked]")
    assert a1.value.startswith("edit")
    # Row 2 is about the new user: expect a "new" action:
    a2 = html.find(".//input[@name='action-2'][@checked]")
    assert a2.value == "new"


@pytest.mark.django_db
def test_si_imu_upload_two_identical_lines(
    article_journal,
    client,
    admin,
    existing_user,
    special_issue,
):
    """Detect two identical contributions (same title and author).

    Refuse to process the second.
    """
    client.force_login(admin)
    url = reverse("si-imu-1", kwargs={"pk": special_issue.id})

    # foglio 2: "Main session" + 2 contributi uguali tra loro (stesso
    # autore e titolo). L'autore è già presente nel DB.
    foglio = (
        ("Main session", None, None, None, None, None),
        (
            existing_user.first_name,
            existing_user.middle_name,
            existing_user.last_name,
            existing_user.email,
            existing_user.institution,
            "Title ふう",
        ),
        (
            existing_user.first_name,
            existing_user.middle_name,
            existing_user.last_name,
            existing_user.email,
            existing_user.institution,
            "Title ふう",
        ),
    )
    ods = make_ods(foglio)
    data = dict(
        data_file=ods,
        create_articles_on_import="on",
        match_euristic="optimistic",
        type_of_new_articles=special_issue.allowed_sections.first().id,
    )
    response = client.post(url, data)

    # Preliminary checks
    assert response.status_code == 200
    expectations = (
        "Insert Users — Step 2/3",
        'name="email_1" value="iamsum@example.com"',
        # no `"email_2" value="iamsum@example.com"`: only an error line
        "Title ふう",
    )
    response_content = response.content.decode()
    for expected in expectations:
        assert expected in response_content

    # Interesting checks
    html = lxml.html.fromstring(response_content)
    # Row 0 is for the "partition", we don't care.
    # Row 1 is about the first already exising user: expect an "edit" action:
    a1 = html.find(".//input[@name='action-1'][@checked]")
    assert a1.value.startswith("edit")
    # Row 2 is about the spurious copy-paste: expect an error line
    error_tr = html.find(".//tr[@class='error']")
    # the error line should contain the line data (e.g. the email)...
    assert error_tr.xpath(f"td[text()='{existing_user.email}']")
    # ...and an error message
    error_msg = error_tr.find("td[@class='error']")
    assert error_msg.text == "Line 2 is the same as 1"


@pytest.mark.django_db
def test_si_imu_upload_iequal_emails(
    article_journal,
    client,
    admin,
    existing_user,
    special_issue,
):
    """Suggestions based on email should be case-insensitive.

    Same as foglio 1, but the emails of the existing user in the DB
    and in te ods file are equal only ignoring case
    (uppercase/lowercase).
    """
    client.force_login(admin)
    url = reverse("si-imu-1", kwargs={"pk": special_issue.id})

    case_changed_email = existing_user.email.upper()
    foglio = (
        ("Main session", None, None, None, None, None),
        (
            existing_user.first_name,
            existing_user.middle_name,
            existing_user.last_name,
            case_changed_email,  # ⇦ interesting piece here
            existing_user.institution,
            "Title ふう",
        ),
        ("Novicius", None, "Fabulator", "nfabulator@dmain.net", "Affilia", "Title ばる"),
    )
    ods = make_ods(foglio)
    data = dict(
        data_file=ods,
        create_articles_on_import="on",
        match_euristic="optimistic",
        type_of_new_articles=special_issue.allowed_sections.first().id,
    )
    response = client.post(url, data)

    # Preliminary checks
    assert response.status_code == 200
    expectations = (
        "Insert Users — Step 2/3",
        f'name="email_1" value="{case_changed_email}"',
        'name="email_2" value="nfabulator@dmain.net"',
        "Title ふう",
        "Title ばる",
    )
    response_content = response.content.decode()
    for expected in expectations:
        assert expected in response_content

    # Interesting checks
    html = lxml.html.fromstring(response_content)
    # Row 0 is for the "partition", we don't care.
    # Row 1 is about the first already exising user: expect an "edit" action:
    a1 = html.find(".//input[@name='action-1'][@checked]")
    assert a1.value.startswith("edit")
    # Row 2 is about the new user: expect a "new" action:
    a2 = html.find(".//input[@name='action-2'][@checked]")
    assert a2.value == "new"


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
