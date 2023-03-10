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
RewriteCond %{REQUEST_URI} "!.*pdf$"
RewriteCond %{REQUEST_URI} "!.*epub$"
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


# Issues - managed by Janeway
# From: //jcom.sissa.it/archive/03/03/
# To:   //jcom.sissa.it/issue/97/info/

# Files/galleys - managed by Janeway
# From: https://jcom.sissa.it/sites/default/files/documents/JCOM_1304_2014_E.pdf
# To:   https://jcom.sissa.it/article/1134/galley/2251/download/
# Main galley in citation_pdf_url (for google scholar, must be sibling or the paper's landing page)
# From: https://jcom.sissa.it/archive/20/02/JCOM_2002_2021_A01_en.pdf"
# To:   https://jcom.sissa.it/article/(\d+)/galley/(\d+)/download/"

# TODO
# TODO  /rss.xml? [R=301,L]
# TODO  /archive? [R=301,L]
# TODO  # drupal is: /author/pietro-greco
# TODO  /author/%1-%2-%3-%4? [R=301,L]
# TODO  /author/%1-%2-%3? [R=301,L]
# TODO  /author/%1-%2? [R=301,L]
# TODO  /author/%1-%2? [R=301,L]
# TODO

#


### /Plone

# TODO: verify if needed!
#
# Virtual paths per i meta Highwire
#                          o:       /archive/16/01/JCOM_1601_2017_C01/JCOM_1601_2017_C02
#                          o:       /archive/16/01/JCOM_1601_2017_C01/JCOM_1601_2017_C02.pdf
#
#
# TBV #RewriteRule   "^/archive/.*/(JCOM[^/]+_ATTACH_[^/]+)$" /dl-tracker/download.php [NC,L,E=virtual:/sites/default/files/documents/additional_file/$1]
# TBV #RewriteRule   "^/archive/.*/(JCOM[^/]+\.pdf)"          /dl-tracker/download.php [NC,L,E=virtual:/sites/default/files/documents/$1]
# TBV ##
# TBV ## Questo lo facciamo come redirect:
# TBV #RewriteRule   "^(/archive/.+/.+/.+).abstract"          https://%{SERVER_NAME}$1                          [R=302,L]
# TBV #
# TBV ## TODO: drop this and rely on Janeway's own metrics (see
# TBV ## e.g. journal.urls.urlpatterns l.35 and
# TBV ## journal.views.download_galley)
# TBV ##
# TBV ## Direct download catcher
# TBV ##------------------------
# TBV ## NOTE: cannot be placed in the <Directory "/var/www/hosts/medialab"> section because
# TBV ##       would be overridden by Drupal's .htaccess
# TBV #RewriteCond %{REQUEST_FILENAME} ".(pdf|epub)$"
# TBV #RewriteRule ^ /dl-tracker/download.php [L]
# TBV #
