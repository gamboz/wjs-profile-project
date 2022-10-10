"""Configure this application."""
# https://docs.djangoproject.com/en/4.0/ref/applications/
from django.apps import AppConfig

from events import logic as events_logic

from .events.wjs_events import notify_coauthors_article_submission


class JCOMProfileConfig(AppConfig):
    """Configuration for this django app."""

    name = "wjs.jcom_profile"
    verbose_name = "WJS JCOM profile"

    def ready(self):
        """Call during initialization."""
        from wjs.jcom_profile import signals, urls

        self.register_hooks()

        events_logic.Events.register_for_event(
            events_logic.Events.ON_ARTICLE_SUBMITTED,
            notify_coauthors_article_submission,
        )

    def register_hooks(self):
        """Register my functions to Janeway's hooks."""
        hooks = [
            # dict(nav_block=dict(module='wjs.jcom_profile.hooks',
            #                     function='prova_hook')),
            dict(
                extra_corefields=dict(
                    module="wjs.jcom_profile.hooks", function="prova_hook"
                )
            ),
        ]
        # NB: do not `import core...` before `ready()`,
        # otherwise django setup process breaks
        from core import plugin_loader

        plugin_loader.register_hooks(hooks)
