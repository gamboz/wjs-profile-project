"""Assignment events functions, that are called when an article is submitted.

Journal level configuration is made using the 'WJS_ARTICLE_ASSIGNMENT_FUNCTIONS' setting
"""
from django.conf import settings
from django.utils.module_loading import import_string


def default_assign_editors_to_articles(**kwargs) -> None:
    """Assign editors to article for review. Default algorithm."""
    from review.models import EditorAssignment

    from ..models import EditorAssignmentParameters

    article = kwargs["article"]
    if article.articlewrapper.special_issue and article.articlewrapper.special_issue.editors:
        parameters = EditorAssignmentParameters.objects.filter(
            journal=article.journal,
            editor__in=article.articlewrapper.special_issue.editors.all(),
        )
    else:
        parameters = EditorAssignmentParameters.objects.filter(journal=article.journal)
    if parameters:
        editor = parameters.order_by("workload").first().editor
        EditorAssignment.objects.create(article=article, editor=editor, editor_type="Editor", notified=True)
        article.stage = "Assigned"
        article.save()
    else:
        print("No editor parameters.")


def jcom_assign_editors_to_articles(**kwargs):
    """Assign editors to article for review. JCOM algorithm."""
    from core.models import AccountRole, Role
    from review.models import EditorAssignment

    from ..models import EditorAssignmentParameters

    article = kwargs["article"]
    directors = AccountRole.objects.filter(
        journal=article.journal,
        role=Role.objects.get(slug="director"),
    ).values_list("user")
    parameters = None
    if article.articlewrapper.special_issue and article.articlewrapper.special_issue.editors:
        parameters = EditorAssignmentParameters.objects.filter(
            journal=article.journal,
            editor__in=article.articlewrapper.special_issue.editors.all(),
        )
    elif directors:
        parameters = EditorAssignmentParameters.objects.filter(journal=article.journal, editor__in=directors)
    if parameters:
        editor = parameters.order_by("workload").first().editor
        EditorAssignment.objects.create(article=article, editor=editor, editor_type="Editor", notified=True)
        article.stage = "Assigned"
        article.save()
    else:
        print("No editor parameters.")


def dispatch_assignment(**kwargs) -> None:
    """Dispatch editors assignment on journal basis, selecting the requested assignment algorithm."""
    journal = kwargs["article"].journal.code
    if journal in settings.WJS_ARTICLE_ASSIGNMENT_FUNCTIONS:
        import_string(settings.WJS_ARTICLE_ASSIGNMENT_FUNCTIONS.get(journal))(**kwargs)
    else:
        import_string(settings.WJS_ARTICLE_ASSIGNMENT_FUNCTIONS.get(None))(**kwargs)
