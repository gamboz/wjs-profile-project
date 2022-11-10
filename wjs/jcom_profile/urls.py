"""My URLs. Looking for a way to "enrich" Janeway's `edit_profile`."""

from core import include_urls
from django.conf.urls import url
from submission import views as submission_views

from wjs.jcom_profile import views

urlpatterns = [
    url(r"^(?P<type>[-\w.]+)/start/$", views.start, name="submission_start"),
    url(r"^profile/$", views.prova, name="core_edit_profile"),
    url(r"^register/step/1/$", views.register, name="core_register"),
    url(
        r"^register/activate/gdpr/(?P<token>.+)/",
        views.confirm_gdpr_acceptance,
        name="accept_gdpr",
    ),
    # Override submission's second step defined in submission.url ...
    # (remember that core.include_url adds a "prefix" to the pattern,
    # here "submit/")
    url(
        r"^submit/(?P<article_id>\d+)/info/$",
        views.SpecialIssues.as_view(),
        name="submit_info",
    ),
    # ... and "rename" it (i.e. the submission's second step) to be
    # able to get back in the loop
    url(
        r"^submit/(?P<article_id>\d+)/info-metadata/$",
        submission_views.submit_info,
        name="submit_info_original",
    ),
    # Special Issues mgmt
    url(r"^si/new$", views.SICreate.as_view(template_name="si_new.html"), name="si-create"),
    url(r"^si/(?P<pk>\d+)/$", views.SIDetails.as_view(template_name="si_details.html"), name="si-details"),
    url(r"^si/(?P<pk>\d+)/edit$", views.SIUpdate.as_view(template_name="si_update.html"), name="si-update"),
    url(
        r"^si/(?P<special_issue_id>\d+)/file/(?P<file_id>\d+)/",
        views.serve_special_issue_file,
        name="special_issue_file_download",
    ),
    url(
        r"^si_file_upload/(?P<special_issue_id>\d+)/",
        views.SIFileUpload.as_view(),
        name="special_issue_file_upload",
    ),
]

urlpatterns.extend(include_urls.urlpatterns)
include_urls.urlpatterns = urlpatterns
