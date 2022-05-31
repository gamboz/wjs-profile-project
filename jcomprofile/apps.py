from django.apps import AppConfig


class JCOMProfileConfig(AppConfig):
    """Configuration for this django app."""

    name = "jcomprofile"
    verbose_name = 'WJS JCOM profile'

    def ready(self):
        """Call during initialization."""
        from jcomprofile import signals
        # from jcomprofile import monkey_patching
        from jcomprofile import urls
