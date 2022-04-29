from django.apps import AppConfig


class JCOMProfileConfig(AppConfig):
    """Configuration for this django app."""

    name = "wjs_jcom_profile"
    verbose_name = 'WJS JCOM profile'

    def ready(self):
        """Call during initialization."""
        from wjs_jcom_profile import signals
        # from wjs_jcom_profile import monkey_patching
        from wjs_jcom_profile import urls
