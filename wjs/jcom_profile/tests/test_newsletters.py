import datetime
import random

import pytest
from django.core import mail, management
from submission.models import Article

from wjs.jcom_profile.models import Recipient


def select_random_keywords(keywords):
    return random.sample(list(keywords), random.randint(1, len(keywords)))


@pytest.mark.django_db
def test_no_newsletters_must_be_sent_when_no_new_articles_with_interesting_keywords_and_news_exist(
    account_factory,
    article_factory,
    news_item_factory,
    recipient_factory,
    section_factory,
    newsletter_factory,
    keyword_factory,
    keywords,
    journal,
):
    newsletter = newsletter_factory()
    users = []
    correspondence_author = account_factory()
    for _ in range(10):
        users.append(account_factory())
    for _ in range(10):
        news_item_factory(
            posted=datetime.datetime.now() + datetime.timedelta(days=-2),
        )
    for user in users:
        recipient = recipient_factory(
            user=user,
        )
        selected_keywords = select_random_keywords(keywords)
        for keyword in selected_keywords:
            recipient.topics.add(keyword)
        recipient.save()
    for i in range(5):
        article = article_factory(
            journal=journal,
            date_published=datetime.datetime.now() + datetime.timedelta(days=1),
            stage="Published",
            correspondence_author=correspondence_author,
            section=section_factory(),
        )
        article.keywords.add(keyword_factory(word=f"{i}-no"))
        article.keywords.add(keyword_factory(word=f"{i}-interesting"))
        article.save()

    management.call_command("send_newsletter_notifications")

    newsletter.refresh_from_db()
    assert newsletter.last_sent.date() == datetime.datetime.now().date()
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_newsletters_are_correctly_sent(
    account_factory,
    article_factory,
    news_item_factory,
    recipient_factory,
    section_factory,
    newsletter_factory,
    keywords,
    journal,
):
    newsletter = newsletter_factory()
    users = []
    correspondence_author = account_factory()
    for _ in range(10):
        users.append(account_factory())
    for _ in range(10):
        news_item_factory(
            posted=datetime.datetime.now() + datetime.timedelta(days=1),
        )
    for user in users:
        recipient = recipient_factory(user=user)
        selected_keywords = select_random_keywords(keywords)
        for keyword in selected_keywords:
            recipient.topics.add(keyword)
        recipient.save()
    for _ in range(50):
        article = article_factory(
            journal=journal,
            date_published=datetime.datetime.now() + datetime.timedelta(days=1),
            stage="Published",
            correspondence_author=correspondence_author,
            section=section_factory(),
        )
        article_keywords = select_random_keywords(keywords)
        for keyword in article_keywords:
            article.keywords.add(keyword)
        article.save()

    management.call_command("send_newsletter_notifications")

    newsletter.refresh_from_db()
    assert newsletter.last_sent.date() == datetime.datetime.now().date()
    filtered_articles = Article.objects.filter(date_published__date__gt=datetime.datetime.now())
    emailed_subscribers = Recipient.objects.filter(topics__in=filtered_articles.values_list("keywords"))
    assert len(mail.outbox) == emailed_subscribers.count()


@pytest.mark.django_db
def test_newsletters_with_news_items(
    account_factory,
    recipient_factory,
    newsletter_factory,
    keywords,
    news_item_factory,
    journal,
):
    newsletter = newsletter_factory()
    news_user, no_news_user = account_factory(email="news@news.it"), account_factory(email="nonews@nonews.it")

    news_recipient = recipient_factory(user=news_user, news=True)
    news_item_factory(
        posted=datetime.datetime.now() + datetime.timedelta(days=1),
    )
    recipient_factory(user=no_news_user, news=False)

    management.call_command("send_newsletter_notifications")

    assert newsletter.last_sent.date() == datetime.datetime.now().date()
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [news_recipient.user.email]
