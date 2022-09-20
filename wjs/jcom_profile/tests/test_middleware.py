"""Tests related to the if-no-gdpr-acknowledged-redirect-me middleware."""
import pytest
from core.models import Account
from django.test import Client


def test_anonymous_can_navigate(journalPippo):
    """Test that anonymous users can navigate.

    Here "anonymous" means not logged in.
    """
    client = Client()
    response = client.get("/contact/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_normal_user_can_navigate(journalPippo):
    """Test that a normal user can navigate normally.

    A normal user has acknowledged our privay policy (i.e. checkbox is
    selected).

    """
    # https://stackoverflow.com/a/39742798/1581629
    client = Client()
    user = Account.objects.get_or_create(username="testuser")[0]
    user.jcomprofile.gdpr_checkbox = True
    user.save()
    client.force_login(user)

    response = client.get("/contact/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_shy_user_cannot_navigate(journalPippo):
    """Test that a user that didn't acknowledge privacy cannot navigate."""
    # check this also:
    # https://flowfx.de/blog/test-django-with-selenium-pytest-and-user-authentication/
    client = Client()
    user = Account.objects.get_or_create(username="testuser")[0]
    user.jcomprofile.gdpr_checkbox = False
    user.save()
    client.force_login(user)

    response = client.get("/contact/")
    assert response.status_code == 302


@pytest.mark.django_db
def test_shy_user_cannot_navigate_bis(journalPippo, client):
    """Test that a user that didn't acknowledge privacy cannot navigate."""
    # https://pytest-django.readthedocs.io/en/latest/helpers.html#client-django-test-client
    username = "user1"
    password = "bar"
    email = "e@mail.it"
    user = Account.objects.create_user(
        username=username, password=password, email=email
    )
    user.jcomprofile.gdpr_checkbox = False
    user.save()
    client.login(username=username, password=password)
    # client.force_login(user)

    response = client.get("/contact/")
    assert response.status_code == 302
