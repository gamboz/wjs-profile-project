"""Management command to add a role."""
import datetime
from typing import List

from comms.models import NewsItem
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from submission.models import Article

from wjs.jcom_profile.models import Newsletter, Recipient


class Command(BaseCommand):
    help = "Send newsletter to enrolled users. This command is intended to be used via a cron task."  # noqa

    def render_and_send_newsletter(
        self,
        subscriber: Recipient,
        rendered_articles: List[str],
        rendered_news: List[str],
    ):
        """
        Send the newsletter email to subscriber.

        :param subscriber: The subscriber Recipient model.
        :param rendered_articles: The articles to be rendered in newsletter email.
        :param rendered_news: The news to be rendered in newsletter emails.
        """
        from premailer import transform

        newsletter_content = render_to_string(
            "newsletter_template.html",
            {"subscriber": subscriber.user, "articles": "".join(rendered_articles), "news": "".join(rendered_news)},
        )
        processed = transform(newsletter_content)

        send_mail(
            f"{subscriber.journal} journal newsletter - {datetime.date.today()}",
            processed,
            settings.DEFAULT_FROM_EMAIL,
            [subscriber.user.email],
            fail_silently=False,
        )

    def handle(self, *args, **options):
        """
        Command entry point.

        Use the unique Newsletter object (creating it if non-existing) to filter articles and news to be sent
        to users based on the last time newsletters have been delivered. Each user is notified considering their
        interests (i.e. topics saved in their Recipient object).
        """
        newsletter, created = Newsletter.objects.get_or_create()
        last_sent = newsletter.last_sent
        if created:
            self.stdout.write(
                self.style.WARNING("A Newsletter object has been created."),
            )
        filtered_articles = Article.objects.filter(date_published__date__lt=last_sent)
        filtered_news = NewsItem.objects.filter(posted__date__gt=last_sent)
        filtered_subscribers = Recipient.objects.filter(topics__in=filtered_articles.values_list("keywords"))
        articles_list = list(filtered_articles)
        for subscriber in filtered_subscribers:
            rendered_articles = []
            rendered_news = []
            for article in articles_list:
                if article.keywords.intersection(subscriber.topics.all()):
                    rendered_articles.append(render_to_string("newsletter_article.html", {"article": article}))
            if subscriber.news:
                for news in filtered_news:
                    rendered_news.append(render_to_string("newsletter_news.html", {"news": news}))

            self.render_and_send_newsletter(subscriber, rendered_articles, rendered_news)
        newsletter.save()

        for article in articles_list:
            article.rendered = render_to_string("newsletter_article.html", {"article": article})
