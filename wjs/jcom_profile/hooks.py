"""Hooks."""
from django.template.loader import render_to_string


def prova_hook(request_context):
    """Test hooks."""
    # TODO: drop me and use django blocks
    template_name = "field.html"
    context = {"form": request_context.get("form"), "journal_settings": request_context.get("journal_settings")}
    rendered = render_to_string(template_name, context)
    return rendered


def extra_edit_profile_parameters_hook(request_context):
    """Add hook to add assignment parameter card."""
    user = request_context.request.user
    journal = request_context.request.journal
    rendered = ""
    if user and journal and user.check_role(journal, "editor"):
        template_name = "extra_edit_profile_card_block.html"
        rendered = render_to_string(
            template_name,
            {
                "card_title": "Edit assignment parameters",
                "card_paragraph": "Go to your your assignment parameters by clicking the button below.",
                "url_name": "assignment_parameters",
                "button_text": "Assignment parameters",
            },
        )
    return rendered


def extra_edit_subscription_hook(request_context):
    """Add hook to add newsletters card."""
    template_name = "extra_edit_profile_card_block.html"
    rendered = render_to_string(
        template_name,
        {
            "card_title": "Newsletters",
            "card_paragraph": "Edit your subscription settings by clicking the button below.",
            "url_name": "edit_newsletters",
            "button_text": "Edit my subscription",
        },
    )
    return rendered
