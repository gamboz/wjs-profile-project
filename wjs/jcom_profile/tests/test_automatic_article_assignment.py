"""Tests related to the submission process."""
import random

import pytest
from django.test import Client, override_settings
from django.urls import reverse
from review.models import EditorAssignment

from wjs.jcom_profile.models import EditorAssignmentParameters

WJS_ARTICLE_ASSIGNMENT_FUNCTIONS = {
    None: "wjs.jcom_profile.events.assignment.default_assign_editors_to_articles",
}


def get_expected_editor(editors, article):
    lowest_workload = 1000
    selected_editor = None
    for editor in editors:
        params = EditorAssignmentParameters.objects.create(
            editor=editor,
            journal=article.journal,
            workload=random.randint(1, 10),
        )
        if params.workload < lowest_workload:
            selected_editor = params.editor
            lowest_workload = params.workload
    return selected_editor


@pytest.mark.parametrize(
    "journal_assignment_algorithm_exists",
    (
        True,
        False,
    ),
)
@pytest.mark.django_db
def test_normal_issue_articles_automatic_assignment(
    admin,
    article,
    directors,
    coauthors_setting,
    journal_assignment_algorithm_exists,
):
    if journal_assignment_algorithm_exists:
        WJS_ARTICLE_ASSIGNMENT_FUNCTIONS[
            article.journal
        ] = "wjs.jcom_profile.events.assignment.jcom_assign_editors_to_articles"
    with override_settings(WJS_ARTICLE_ASSIGNMENT_FUNCTIONS=WJS_ARTICLE_ASSIGNMENT_FUNCTIONS):
        client = Client()
        client.force_login(admin)
        selected_director = get_expected_editor(directors, article)

        url = reverse("submit_review", args=(article.pk,))

        response = client.post(url, data={"next_step": "next_step"})
        assert response.status_code == 302

        editor_assignment = EditorAssignment.objects.get(article=article)
        article.refresh_from_db()

        assert editor_assignment.editor == selected_director
        assert article.stage == "Assigned"


@pytest.mark.parametrize(
    "journal_assignment_algorithm_exists",
    (
        True,
        False,
    ),
)
@pytest.mark.django_db
def test_special_issue_articles_automatic_assignment(
    admin,
    article,
    coauthors_setting,
    special_issue,
    journal_assignment_algorithm_exists,
):
    if journal_assignment_algorithm_exists:
        WJS_ARTICLE_ASSIGNMENT_FUNCTIONS[
            special_issue.journal.code
        ] = "wjs.jcom_profile.events.assignment.jcom_assign_editors_to_articles"
    with override_settings(WJS_ARTICLE_ASSIGNMENT_FUNCTIONS=WJS_ARTICLE_ASSIGNMENT_FUNCTIONS):
        client = Client()
        client.force_login(admin)
        selected_editor = get_expected_editor(special_issue.editors.all(), article)

        url = reverse("submit_review", args=(article.pk,))

        response = client.post(url, data={"next_step": "next_step"})
        assert response.status_code == 302

        editor_assignment = EditorAssignment.objects.get(article=article)
        article.refresh_from_db()

        assert editor_assignment.editor == selected_editor
        assert article.stage == "Assigned"
