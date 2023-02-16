import datetime
import random

import pytest
from conftest import yesterday
from django.core import management


def select_random_keywords(keywords):
    return random.sample(list(keywords), random.randint(1, len(keywords)))


@pytest.mark.django_db
def test_newsletters_are_correctly_sent(
    account_factory,
    article_factory,
    news_item_factory,
    recipient_factory,
    section_factory,
    keywords,
    newsletter,
    journal,
):
    users, recipients, articles, news_items = [], [], [], []
    correspondence_author = account_factory()
    for _ in range(10):
        users.append(account_factory())
    for _ in range(10):
        news_items.append(news_item_factory())
    for user in users:
        recipient = recipient_factory(user=user)
        selected_keywords = select_random_keywords(keywords)
        for keyword in selected_keywords:
            recipient.topics.add(keyword)
        recipient.save()
        recipients.append(recipient)
    for _ in range(50):
        article = article_factory(
            journal=journal,
            date_published=yesterday,
            stage="Published",
            correspondence_author=correspondence_author,
            section=section_factory(),
        )
        article_keywords = select_random_keywords(keywords)
        for keyword in article_keywords:
            article.keywords.add(keyword)
        article.save()
        articles.append(article)

    management.call_command("send_newsletter_notifications")

    newsletter.refresh_from_db()
    assert newsletter.last_sent.date() == datetime.datetime.now().date()
