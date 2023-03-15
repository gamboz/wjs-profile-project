"""Test that the generation of the DOIs respect the specs."""

from ..utils import generate_doi


def test_doi_generation_jcom(article_fb):
    "Generation of DOI for JCOM respect the specs."
    article = article_fb(
        page_number="A01",
        section="Article",
        # ...
    )
    assert article.get_identifier("doi") is None
    generate_doi(article)
    assert article.get_identifier("doi") == "10123"
