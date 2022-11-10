"""Assignment events functions, that are called when an article is submitted.

Journal level configuration is made using the 'WJS_ARTICLE_ASSIGNMENT_FUNCTIONS' setting
"""
from core.settings import WJS_ARTICLE_ASSIGNMENT_FUNCTIONS  # NOQA
from django.utils.module_loading import import_string


def default_assign_editors_to_articles(**kwargs) -> None:
    """Assign editors to article for review. Default algorithm. Logic TBD."""
    print("default assignment algorithm.")


def dispatch_assignment(**kwargs) -> None:
    """Dispatch editors assignment on journal basis, selecting the requested assignment algorithm."""
    journal = kwargs["article"].journal_id
    if journal in WJS_ARTICLE_ASSIGNMENT_FUNCTIONS:
        import_string(WJS_ARTICLE_ASSIGNMENT_FUNCTIONS.get(journal))(**kwargs)
    else:
        import_string(WJS_ARTICLE_ASSIGNMENT_FUNCTIONS.get(None))(**kwargs)
