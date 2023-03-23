from datetime import timedelta

import pytest
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

from wjs.plugins.wjs_latest_news.plugin_settings import get_plugin_context, WJSLatestArticles

import factory


@pytest.mark.django_db
def test_news_context(fake_request, news_item_factory):
    home_page_element = WJSLatestArticles.create_home_page_elements()

    _now = now()
    news_count = 10
    journal = fake_request.journal
    content_type = ContentType.objects.get_for_model(journal)
    # required to ensure batch object sequence always starts at 0
    news_item_factory.reset_sequence()
    # creating a set of news:
    # sequence in reverse order of creation
    # posted date always set in the past in incremental order
    # start_display date is set in the past (first news is 10 days in the past, second 11 days etc)
    # end_display date is set in the past but only for a subset of news (when index is divisible by 3)
    news_item_factory.create_batch(
        news_count,
        content_type=content_type,
        object_id=journal.pk,
        sequence=factory.Sequence(lambda n: news_count - n),
        posted=factory.Sequence(lambda n: _now - timedelta(days=n)),
        start_display=factory.Sequence(lambda n: _now - timedelta(days=(news_count + n))),
        end_display=factory.Sequence(lambda n: _now - timedelta(days=n) if n % 3 == 0 else None),
    )
    # non journal news, these should not appear in the set of results
    news_item_factory.create_batch(
        news_count,
    )
    context = get_plugin_context(fake_request, [home_page_element])
    assert len(context["wjs_latest_news_list"]) == 7
    assert [n.sequence for n in context["wjs_latest_news_list"]] == [2, 3, 5, 6, 8, 9, 10]
