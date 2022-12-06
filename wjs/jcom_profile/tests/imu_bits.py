"""Bits and pieces used by test-IMU family."""


# foglio 1: "Main session" + 2 contributi diversi (diversi autori e
# titolo). Il primo autore è già presente nel DB.
FOGLIO1 = (
    ("Main session", None, None, None, None, None),
    ("Iam", None, "Sum", "iamsum@example.com", "ML", "Title ふう"),
    ("Novicius", None, "Fabulator", "nfabulator@dmain.net", "Affilia", "Title ばる"),
)
expectations1 = (
    "Insert Users — Step 2/3",
    'name="email_1" value="iamsum@example.com"',
    'name="email_2" value="nfabulator@dmain.net"',
    'checked /><label for="choosen_db00">DB',
    "Title ふう",
    "Title ばる",
)


# foglio 2: "Main session" + 2 contributi uguali tra loro (stesso
# autore e titolo). L'autore è già presente nel DB.
FOGLIO2 = (
    ("Main session", None, None, None, None, None),
    ("Iam", None, "Sum", "iamsum@example.com", "ML", "Title ふう"),
    ("Iam", None, "Sum", "iamsum@example.com", "ML", "Title ふう"),
)
# The interesting thing here is that the system will detect two
# identical contributions (same session, title, and author) and refuse
# to process the second.
expectations2 = (
    "Check and choose",
    'checked /><label for="choosen_db00">DB',
    '<td class="err">already seen!<br/>line ignored</td>',
    "Title ふう",
    "mailto:%(eo_mail_encoded)s",
)


# foglio 3: come foglio 1, ma il primo autore è presente del DB con
# una mail uguale solo se non si consiera il case
# (uppercase/lowercase).
FOGLIO3 = (
    ("Main session", None, None, None, None, None),
    ("Iam", None, "Sum", "Sum@medialab.sissa.it", "ML", "Title ふう"),
    ("Novicius", None, "Fabulator", "nfabulator@dmain.net", "Affilia", "Title ばる"),
)
# Here I want to make sure that emails are compared
# case-insensitive. If that is not so, the first account will receive
# a "checked choosen_new0".
expectations3 = (
    "Check and choose",
    'checked /><label for="choosen_db00">DB',
    'checked /><label for="choosen_new1">new',
    "Title ふう",
    "Title ばる",
    "mailto:%(eo_mail_encoded)s",
)

# foglio 4: "Main session" + 2 contributi diversi dello stesso autore.
#           le mail dell'autore hanno medesimo "CasiNg". L'autore non
#           è presente nel DB.
# Qui il sistema suggerisce "new" per entrambi.
#
# Successivamente, il sistema si accorge che il secondo contributo è
# dello stesso autore del primo contributo e ri-utilizza l'account
# creato per il primo contributo. Questo però va testato da qualche
# altra parte.
FOGLIO4 = (
    ("Main session", None, None, None, None, None),
    ("Iam", None, "Sum", "matteo@nonexist.sissa.it", "ML", "Title ふう"),
    ("Iam", None, "Sum", "matteo@nonexist.sissa.it", "ML", "Title ばる"),
)
expectations4 = (
    "Check and choose",
    'checked /><label for="choosen_new0">new',
    'checked /><label for="choosen_new1">new',
    "Title ふう",
    "Title ばる",
    "mailto:%(eo_mail_encoded)s",
)

# foglio 5: come foglio4, ma le due mail dell'autore sono scritte con
#           "CasiNg" diverso. L'autore non è presente nel DB.  Qui il
#           sistema suggerisce "new" per entrambi.
FOGLIO5 = (
    ("Main session", None, None, None, None, None),
    ("Iam", None, "Sum", "matteo@nonexist.sissa.it", "ML", "Title ふう"),
    ("Iam", None, "Sum", "Iam@nonexist.sissa.it", "ML", "Title ばる"),
)
expectations5 = (
    "Check and choose",
    'checked /><label for="choosen_new0">new',
    'checked /><label for="choosen_new1">new',
    "Title ふう",
    "Title ばる",
    "mailto:%(eo_mail_encoded)s",
)
