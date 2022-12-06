"""Bits and pieces used by test-IMU family."""


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
