from django.http import Http404
from django.views.generic import UpdateView

from .plugin_settings import PLUGIN_NAME
from .models import PluginConfig


class ConfigUpdateView(UpdateView):
    model = PluginConfig
    fields = ["title", "count"]

    def get_object(self, queryset=None):
        """
        Get or create the configuration model instance for the current journal.

        If used outside a journal, return 404
        """
        if not queryset:
            queryset = self.get_queryset()
        if self.request.journal:
            try:
                return queryset.get(journal=self.request.journal)
            except PluginConfig.DoesNotExist:
                return PluginConfig.objects.create(journal=self.request.journal)
        else:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["PLUGIN_NAME"] = PLUGIN_NAME
        return context
