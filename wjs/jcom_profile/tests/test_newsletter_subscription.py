import random

import pytest
from django.core import mail
from django.test import Client
from django.test.client import RequestFactory
from django.urls import reverse
from submission.models import Keyword
from utils import setting_handler

from wjs.jcom_profile.models import Recipient
from wjs.jcom_profile.utils import generate_token


@pytest.mark.parametrize("is_news", (True, False))
@pytest.mark.django_db
def test_update_newsletter_subscription(jcom_user, keywords, journal, is_news):
    keywords = random.choices(Keyword.objects.values_list("id", "word"), k=5)

    client = Client()
    client.force_login(jcom_user)
    url = f"/{journal.code}/update/newsletters/"
    data = {"topics": [k[0] for k in keywords], "news": is_news}
    response = client.post(url, data, follow=True)
    assert response.status_code == 200

    user_recipient = Recipient.objects.get(user=jcom_user, journal=journal)
    topics = user_recipient.topics.all()
    for topic in topics:
        assert topic.word in [k[1] for k in keywords]

    messages = list(response.context["messages"])
    assert len(messages) == 1
    assert messages[0].message == "Newsletter preferences updated."


@pytest.mark.django_db
def test_newsletter_unsubscription(jcom_user, keywords, journal):
    client = Client()
    client.force_login(jcom_user)
    url = f"/{journal.code}/update/newsletters/"
    data = {}
    response = client.post(url, data, follow=True)
    assert response.status_code == 200

    user_recipient = Recipient.objects.get(user=jcom_user, journal=journal)
    assert not user_recipient.topics.all()
    assert not user_recipient.news

    messages = list(response.context["messages"])
    assert len(messages) == 1
    assert messages[0].message == "Unsubscription successful."


@pytest.mark.django_db
def test_register_to_newsletter_as_anonymous_user(journal, custom_newsletter_setting):
    client = Client()
    url = f"/{journal.code}/register/newsletters/"
    anonymous_email = "anonymous@email.com"
    newsletter_token = generate_token(anonymous_email)

    response_get = client.get(url)
    request = RequestFactory().get(url)
    assert response_get.status_code == 200

    data = {"email": anonymous_email}
    response_register = client.post(url, data, follow=True)
    redirect_url, status_code = response_register.redirect_chain[-1]

    anonymous_recipient = Recipient.objects.get(email=anonymous_email)

    assert status_code == 302
    assert redirect_url == reverse("register_newsletters_email_sent")
    assert len(mail.outbox) == 1
    newsletter_email = mail.outbox[0]
    acceptance_url = request.build_absolute_uri(
        reverse(
            "confirm_anonymous_newsletter_subscription",
            kwargs={"token": newsletter_token},
        ),
    )
    assert newsletter_email.subject == "Newsletter registration"
    assert newsletter_email.body == setting_handler.get_setting(
        "email",
        "subscribe_custom_email_message",
        journal,
    ).processed_value.format(journal, acceptance_url)
    assert anonymous_recipient.accepted_subscription is False
    assert anonymous_recipient.newsletter_token == newsletter_token


@pytest.mark.django_db
@pytest.mark.parametrize("accepted_subscription", (True, False))
def test_register_to_newsletter_as_anonymous_user_with_existing_recipient(
    journal,
    custom_newsletter_setting,
    accepted_subscription,
):
    client = Client()
    url = f"/{journal.code}/register/newsletters/"
    anonymous_email = "anonymous@email.com"
    newsletter_token = generate_token(anonymous_email)
    anonymous_recipient = Recipient.objects.create(
        email=anonymous_email,
        newsletter_token=newsletter_token,
        journal=journal,
    )
    if accepted_subscription:
        anonymous_recipient.accepted_subscription = True
        anonymous_recipient.save()

    data = {"email": anonymous_email}
    response_register = client.post(url, data, follow=True)
    redirect_url, status_code = response_register.redirect_chain[-1]

    assert status_code == 302
    assert len(mail.outbox) == 0

    anonymous_recipient.refresh_from_db()
    if not accepted_subscription:
        assert redirect_url == reverse("confirm_anonymous_newsletter_subscription", kwargs={"token": newsletter_token})
        assert anonymous_recipient.accepted_subscription is False
    else:
        assert redirect_url == reverse("edit_newsletters")
        assert anonymous_recipient.accepted_subscription is True


@pytest.mark.django_db
def test_confirm_newsletter_subscription_as_anonymous_user(journal, custom_newsletter_setting):
    client = Client()
    anonymous_email = "anonymous@email.com"
    newsletter_token = generate_token(anonymous_email)
    url = reverse("confirm_anonymous_newsletter_subscription", kwargs={"token": newsletter_token})
    anonymous_recipient = Recipient.objects.create(
        email=anonymous_email,
        newsletter_token=newsletter_token,
        journal=journal,
    )
    data = {"accepted_subscription": True}
    response = client.post(url, data, follow=True)
    redirect_url, status_code = response.redirect_chain[-1]

    assert status_code == 302
    anonymous_recipient.refresh_from_db()
    assert redirect_url == reverse("edit_newsletters")
    assert anonymous_recipient.accepted_subscription is True


@pytest.mark.django_db
def test_anonymous_user_newsletter_unsubscription(journal):
    client = Client()
    anonymous_email = "anonymous@email.com"
    newsletter_token = generate_token(anonymous_email)
    anonymous_recipient = Recipient.objects.create(
        email=anonymous_email,
        newsletter_token=newsletter_token,
        journal=journal,
    )
    session = client.session
    session["anonymous_recipient"] = anonymous_recipient.id
    session.save()
    url = f"/{journal.code}/update/newsletters/"
    data = {}
    response = client.post(url, data, follow=True)
    redirect_url, status_code = response.redirect_chain[-1]
    assert status_code == 302
    assert redirect_url == f"/{journal.code}/"

    messages = list(response.context["messages"])
    assert len(messages) == 1
    assert messages[0].message == "Unsubscription successful."

    assert not Recipient.objects.filter(email=anonymous_email, newsletter_token=newsletter_token)
