"""Hooks."""
from django.template.loader import render_to_string


def prova_hook(request_context):
    """Test hooks."""
    # TODO: drop me and use django blocks
    template_name = "field.html"
    context = {"form": request_context.get("form"), "journal_settings": request_context.get("journal_settings")}
    rendered = render_to_string(template_name, context)
    return rendered


def extra_link_hook(request_context):
    """Add hook to add assignment parameter button."""
    template_name = "button_link.html"
    rendered = render_to_string(template_name, {})
    return rendered
