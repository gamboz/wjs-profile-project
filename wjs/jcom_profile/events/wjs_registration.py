from events import logic as events_logic

from wjs.jcom_profile.events.wjs_events import notify_coauthors_article_submission

events_logic.Events.register_for_event(
    events_logic.Events.ON_ARTICLE_SUBMITTED,
    notify_coauthors_article_submission
)
