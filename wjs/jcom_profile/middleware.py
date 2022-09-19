"""Middleware for JCOM account profile."""
from django.contrib import messages
from django.shortcuts import redirect, reverse
from django.urls import resolve
from utils.logger import get_logger

logger = get_logger(__name__)


class PrivacyAcknowledgedMiddleware:
    """Ensure that the logged-in user has acknowledged the privacy policy."""

    # TODO: probably the callable-class system is post-django1.11
    # def __init__(self, get_response):
    #     """One-time configuration and initialization."""
    #     self.get_response = get_response

    # def __call__(self, request):
    @staticmethod  # is this needed???
    def process_request(request):
        """Ensure that the logged-in user has acknowledged the privacy policy.

        Kick in only if there is a logged-in user (otherwise return None).
        Let alone /logout and /profile.

        If the logged-in user hasn't got a gdpr_policy flag, set a
        flash message and redirect to /profile.

        """
        logger.debug("Privacy middleware")
        if not hasattr(request, "user"):
            return None

        # The following fails on <J-CODE>/profile
        # if request.path in ("/logout/", "/profile/"): <--
        # import ipdb; ipdb.set_trace()

        # The following fails on <J-CODE>/*
        # (does the resolver know about journals?)
        # match = resolve(request.path)
        # if match.url_name in (
        #     "core_edit_profile",
        #     "core_logout",
        # ):
        if request.path.endswith("/logout/") or request.path.endswith(
            "/profile/"
        ):
            return None

        # TODO: do I need `if request.user.is_authenticated`?
        if not request.user.is_authenticated:
            return None

        if hasattr(request.user, "jcom_profile"):
            if request.user.jcom_profile.gdpr_policy:
                return None

        # TODO: parametrize message text in journal settings?
        message_text = """Please acknowledge privacy note (see checkbox below)
        or log-out to continue navigate the site.
        """
        # TODO: the flash message is almost invisible in some theme (OLH?)
        # TODO: the flash message can be too fast. Trying to add extra
        # tags to slow it down at js level.
        messages.add_message(
            request,
            messages.WARNING,
            message_text,
            extra_tags="ciao-tag,ciaone",  # not honored by themes?
        )
        logger.debug(
            f"Redirecting {request.user.id} to profile page to acknowledge privacy."
        )
        return redirect(reverse("core_edit_profile"), permanent=False)
