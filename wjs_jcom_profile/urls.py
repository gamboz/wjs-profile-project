"""My URLs. Looking for a way to "enrich" Janeway's `edit_profile`."""

from django.conf.urls import url
from plugins.wjs_jcom_profile import views


urlpatterns = [
    url(r'^profile/$', views.prova, name='core_edit_profile'),
    # url(r'^prova/$', views.prova, name='core_edit_profile'),
]
