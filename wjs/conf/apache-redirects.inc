# JCOM redirects
# - manage old "incarnations"
# - virtual path PDF of published articles for Google Scholar
# - allow  matomo to keep track of downloads via diret link (TBV)

RewriteEngine On


# Tryed references by name (https://pcre.org/current/doc/html/pcre2syntax.html#SEC22).
# These fail:
# (?P=pubid)
# \k<pubid>
# \k'pubid'
# \g{pubid}
# ...
# and then I abandoned the idea of backreference by name... sigh...

# Important! Papers' landing page
# From: //jcom.sissa.it/archive/13/04/JCOM_1304_2014_E
# To:   //jcom.sissa.it/article/pubid/JCOM_1304_2014_E
RewriteRule "^/archive/(?<volume>\d{2})/(?<issue>\d{2})/(?<pubid>[\w.()-]+)(?<rest>.*)$" "/article/pubid/$3$4" [R=301,L]


# Drop redirects for URLs pre-2015
# E.g.
# - //jcom.sissa.it/jcom0303.html
# - //jcom.sissa.it/comment/com020102_or.html
# - //jcom.sissa.it/archive/13/04/JCOM_1304_2014_E/JCOM_1304_2014_E.pdf
# - //jcom.sissa.it/all-articles/RSS$
# - //jcom.sissa.it/search_rss.*
# - //jcom.sissa.it/.*atct_topic_view.*
# - //jcom.sissa.it/all/.*
# - //jcom.sissa.it/mc-logo.png
# - //jcom.sissa.it/contentsof.*
# - //jcom.sissa.it/to-submit/submissionform.*


# Issue
# From: //jcom.sissa.it/archive/03/03/
# To:   //jcom.sissa.it/issue/97/info/
# Managed by Janeway


# TODO
# TODO  /rss.xml? [R=301,L]
# TODO  /archive? [R=301,L]
# TODO  # drupal is: /author/pietro-greco
# TODO  /author/%1-%2-%3-%4? [R=301,L]
# TODO  /author/%1-%2-%3? [R=301,L]
# TODO  /author/%1-%2? [R=301,L]
# TODO  /author/%1-%2? [R=301,L]
# TODO

# Files/galleys
# From: https://jcom.sissa.it/sites/default/files/documents/JCOM_1304_2014_E.pdf
# To:   https://jcom.sissa.it/article/1134/galley/2251/download/
#
# {as} 2017-06-13: spostato nel backend, dove faccio /quasi/ la stessa cosa,
#                  mettendo in un meta l'url in /archive...
#                  Caveat:
#                   in plone erano:  /archive/13/04/JCOM_1304_2014_E/JCOM_1304_2014_E.pdf
#                   ma Google vuole: /archive/13/04/JCOM_1304_2014_E.pdf
#
#RewriteRule ^/archive/.+/([^/]+.pdf)$   /sites/default/files/documents/$1 [R,L]


### /Plone

# TODO: verify if needed!
#
# Virtual paths per i meta Highwire
# ---------------------------------
#   Il PDF (e gli altri allegati) _devono_ stare nello stesso folder dei metadati:
#
# Physical PDF (Drupal upload dir): /sites/default/files/documents/JCOM_1601_2017_E.pdf
#
# Metadata (landing page) in:       /archive/16/01/JCOM_1601_2017_E
#                          o:       /archive/16/01/JCOM_1601_2017_C01/JCOM_1601_2017_C02
#        o (articoli vecchi):       /archive/01/01/E0101
# Virtual PDF (per Google):         /archive/16/01/JCOM_1601_2017_E.pdf
#                          o:       /archive/16/01/JCOM_1601_2017_C01/JCOM_1601_2017_C02.pdf
#        o (articoli vecchi):       /archive/01/01/jcom0101%282002%29E.pdf
#
# Soddisfiamo anche:
#      - i vecchi path Plone:       /archive/16/01/JCOM_1601_2017_E/JCOM_1601_2017_E.pdf
#
# Nota infine che pare non ci sia modo di passare il PT al dl-tracker con la url riscritta
# (senza fare un redirect visibile), quindi chiamiamo il tracker direttamente con il path
# da servire, utilizzando una env-var
# Se non ci fosse il tracker, basterebbero dei [NC,PT,L] al path fisico
#
RewriteRule   "^/archive/.*/(JCOM[^/]+_ATTACH_[^/]+)$" /dl-tracker/download.php [NC,L,E=virtual:/sites/default/files/documents/additional_file/$1]
RewriteRule   "^/archive/.*/(JCOM[^/]+\.pdf)"          /dl-tracker/download.php [NC,L,E=virtual:/sites/default/files/documents/$1]
#
# Questo lo facciamo come redirect:
RewriteRule   "^(/archive/.+/.+/.+).abstract"          https://%{SERVER_NAME}$1                          [R=302,L]

# TODO: drop this and rely on Janeway's own metrics (see
# e.g. journal.urls.urlpatterns l.35 and
# journal.views.download_galley)
#
# Direct download catcher
#------------------------
# NOTE: cannot be placed in the <Directory "/var/www/hosts/medialab"> section because
#       would be overridden by Drupal's .htaccess
RewriteCond %{REQUEST_FILENAME} ".(pdf|epub)$"
RewriteRule ^ /dl-tracker/download.php [L]
