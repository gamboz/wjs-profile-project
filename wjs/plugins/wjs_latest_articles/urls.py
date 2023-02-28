from django.conf.urls import url

from .plugin_settings import MANAGER_URL
from . import views


urlpatterns = [
    url(r'^manager/$', views.ConfigUpdateView.as_view(), name=MANAGER_URL),
]
