"""WJS tags."""
from django import template
from submission.models import Article

from wjs.jcom_profile.models import SpecialIssue

register = template.Library()


@register.simple_tag
def journal_has_open_si(journal):
    """Return true if this journal has any special issue open for submission."""
    # The timeline.html template should show/hide the SI step as
    # necessary.
    has_open_si = SpecialIssue.objects.current_journal().open_for_submission().current_user().exists()
    return has_open_si


@register.filter
def keyvalue(dictionary, key):
    """Return the value of dict[key]."""
    return dictionary[key]


@register.filter
def article(article_wrapper):
    """Return the article wrapped by the given article_wrapper."""
    # I don't know why, but simply calling
    # `article_wrapper.janeway_article` results in an error
    # `'ArticleWrapper' object has no attribute 'id'`
    return Article.objects.get(pk=article_wrapper.janeway_article_id)


@register.filter
def has_attr(obj, attr):
    """Return True is the given object has the given attribute.

    Example usage: {% if article|has_attr:"genealogy" %}
    """
    return hasattr(obj, attr)


@register.filter
def how_to_cite(article):
    """Return APA-style how-to-cite for JCOM."""
    authors = article.frozenauthor_set.all()
    author_str = " & ".join(a.citation_name() for a in authors)
    htc = f"""{author_str}, ({article.date_published.year}).
    {article.title} <i>{article.journal.code}</i>
    {article.issue.volume}({article.issue.issue}), {article.page_numbers}.
    https://doi.org/{article.get_doi()}
    """
    return htc
