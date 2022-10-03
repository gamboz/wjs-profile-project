from django.urls import reverse

from events import logic as events_logic
from utils import (notify_helpers, setting_handler)


def example_event_func(**kwargs):
    # FIXME: This logic is intended to be insert in janeway; this is a copy-paste of janeway
    #  src/utils/transitional_email.send_submission_acknowledgement function, with the difference that we want to
    #  notify coauthors
    # TODO: Create a data migration for following settings: submission_coauthors_acknowledgment,
    #  subject_submission_coauthors_acknowledgement
    article = kwargs['article']
    request = kwargs['request']
    coauthors = [c for c in article.authors.all() if c != article.correspondence_author]

    # generate URL
    review_unassigned_article_url = request.journal.site_url(
        path=reverse(
            'review_unassigned_article',
            kwargs={'article_id': article.pk},
        )
    )

    log_dict = {
        'level': 'Info',
        'action_text': 'A new article {0} was submitted'.format(article.title),
        'types': 'New Submission Acknowledgement',
        'target': article,
    }

    # send to coauthors
    for coauthor in coauthors:
        context = {
            'article': article,
            'request': request,
            'author': coauthor,
            'review_unassigned_article_url': review_unassigned_article_url,
        }
        notify_helpers.send_email_with_body_from_setting_template(
            request,
            'submission_coauthors_acknowledgment',
            'subject_submission_coauthors_acknowledgement',
            [coauthor.email],
            context,
            log_dict=log_dict,
        )


events_logic.Events.register_for_event(
    events_logic.Events.ON_ARTICLE_SUBMITTED,
    example_event_func
)
