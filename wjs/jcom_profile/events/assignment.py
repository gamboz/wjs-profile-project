"""Assignment events functions, that are called when an article is submitted.

Journal level configuration is made using the 'WJS_ARTICLE_ASSIGNMENT_FUNCTIONS' setting
"""


def assign_editors_to_articles(**kwargs) -> None:
    """Assign editors to article or review. Default algorithm. Logic TBD."""
    print("editor assigned")
