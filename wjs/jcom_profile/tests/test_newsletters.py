import datetime
import random

import pytest
from comms.models import NewsItem
from django.core import mail, management
from submission.models import Article

from wjs.jcom_profile.models import Recipient


def select_random_keywords(keywords):
    return random.sample(list(keywords), random.randint(1, len(keywords)))


def check_email_body(outbox):
    for email in outbox:
        user_email = email.to[0]
        user_keywords = Recipient.objects.get(user__email=user_email).topics.all()
        for topic in user_keywords:
            articles = Article.objects.filter(keywords__in=[topic], date_published__date__gt=datetime.datetime.now())
            for article in articles:
                assert article.title in email.body
        news_items = NewsItem.objects.filter(posted__date__gt=datetime.datetime.now())
        for item in news_items:
            assert item.title in email.body


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

    check_email_body(mail.outbox)


@pytest.mark.django_db
def test_newsletters_with_news_items_only_must_be_sent(
    account_factory,
    recipient_factory,
    newsletter_factory,
    news_item_factory,
    keywords,
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

    check_email_body(mail.outbox)


@pytest.mark.django_db
def test_newsletters_with_articles_only_must_be_sent(
    account_factory,
    recipient_factory,
    newsletter_factory,
    article_factory,
    section_factory,
    keyword_factory,
    journal,
):
    newsletter = newsletter_factory()
    correspondence_author = account_factory()
    newsletter_user_keyword = keyword_factory()
    newsletter_article_user, no_newsletter_article_user = account_factory(email="article@article.it"), account_factory(
        email="noarticle@article.it",
    )
    newsletter_article = article_factory(
        journal=journal,
        date_published=datetime.datetime.now() + datetime.timedelta(days=1),
        stage="Published",
        correspondence_author=correspondence_author,
        section=section_factory(),
    )
    newsletter_article.keywords.add(newsletter_user_keyword)
    newsletter_article.save()

    no_newsletter_article = article_factory(
        journal=journal,
        date_published=datetime.datetime.now() + datetime.timedelta(days=1),
        stage="Published",
        correspondence_author=correspondence_author,
        section=section_factory(),
    )
    no_newsletter_article.keywords.add(keyword_factory())
    no_newsletter_article.save()

    newsletter_article_recipient = recipient_factory(
        user=newsletter_article_user,
        news=True,
    )
    newsletter_article_recipient.topics.add(newsletter_user_keyword)
    newsletter_article_recipient.save()

    recipient_factory(user=no_newsletter_article_user, news=False)

    management.call_command("send_newsletter_notifications")

    assert newsletter.last_sent.date() == datetime.datetime.now().date()
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [newsletter_article_recipient.user.email]

    check_email_body(mail.outbox)


@pytest.mark.django_db
def test_newsletters_are_correctly_sent_with_both_news_and_articles(
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

    check_email_body(mail.outbox)
