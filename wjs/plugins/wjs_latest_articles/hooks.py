from submission.models import Article
from comms.models import NewsItem


def jcom_home_context(request, homepage_elements):
    return {
        "latest_articles": Article.objects.order_by("-date_published")[:10],
        "latest_news": NewsItem.objects.order_by("-posted")[:10]
    }
