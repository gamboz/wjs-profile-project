"""Assignment events functions, that are called when an article is submitted.

Journal level configuration is made using the 'WJS_ARTICLE_ASSIGNMENT_FUNCTIONS' setting
"""
from core.settings import WJS_ARTICLE_ASSIGNMENT_FUNCTIONS  # NOQA


def default_assign_editors_to_articles(**kwargs) -> None:
    """Assign editors to article for review. Default algorithm. Logic TBD."""
    print("default assignment algorithm.")


def dispatch_assignment(**kwargs) -> None:
    """Dispatch editors assignment on journal basis, selecting the requested assignment algorithm."""
    journal = kwargs["article"].journal_id  # NOQA
    # TODO I cannot figure out how to use dotted path function.
    #  WJS_ARTICLE_ASSIGNMENT_FUNCTIONS.get(journal, WJS_ARTICLE_ASSIGNMENT_FUNCTIONS.get(None))(kwargs) noqa

    default_assign_editors_to_articles(**kwargs)
