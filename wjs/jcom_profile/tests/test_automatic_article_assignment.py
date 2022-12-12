"""Tests related to the submission process."""
import random

import pytest
from django.test import Client, override_settings
from django.urls import reverse
from review.models import EditorAssignment

from wjs.jcom_profile.models import EditorAssignmentParameters


@pytest.mark.django_db
def test_jcom_normal_issue_articles_are_assigned_to_journal_director_with_lowest_workload(
    admin,
    article,
    directors,
    coauthors_setting,
):
    client = Client()
    client.force_login(admin)
    lowest_workload = 1000
    selected_director = None
    for director in directors:
        params = EditorAssignmentParameters.objects.create(
            editor=director,
            journal=article.journal,
            workload=random.randint(1, 10),
        )
        if params.workload < lowest_workload:
            selected_director = params.editor
            lowest_workload = params.workload

    url = reverse("submit_review", args=(article.pk,))

    response = client.post(url, data={"next_step": "next_step"})
    assert response.status_code == 302

    editor_assignment = EditorAssignment.objects.get(article=article)
    article.refresh_from_db()

    assert editor_assignment.editor == selected_director
    assert article.stage == "Assigned"


@pytest.mark.django_db
def test_jcom_special_issue_articles_are_assigned_to_editor_with_lowest_workload_among_special_issue_editors(
    admin,
    article,
    coauthors_setting,
    special_issue,
):
    client = Client()
    client.force_login(admin)
    lowest_workload = 1000
    selected_editor = None
    for editor in special_issue.editors.all():
        params = EditorAssignmentParameters.objects.create(
            editor=editor,
            journal=special_issue.journal,
            workload=random.randint(1, 10),
        )
        if params.workload < lowest_workload:
            selected_editor = params.editor
            lowest_workload = params.workload

    url = reverse("submit_review", args=(article.pk,))

    response = client.post(url, data={"next_step": "next_step"})
    assert response.status_code == 302

    editor_assignment = EditorAssignment.objects.get(article=article)
    article.refresh_from_db()

    assert editor_assignment.editor == selected_editor
    assert article.stage == "Assigned"


@pytest.mark.django_db
@override_settings(
    WJS_ARTICLE_ASSIGNMENT_FUNCTIONS={
        None: "wjs.jcom_profile.events.assignment.default_assign_editors_to_articles",
    },
)
def test_default_normal_issue_articles_are_assigned_to_journal_director_with_lowest_workload(
    admin,
    article,
    editors,
    coauthors_setting,
):
    client = Client()
    client.force_login(admin)
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

    url = reverse("submit_review", args=(article.pk,))

    response = client.post(url, data={"next_step": "next_step"})
    assert response.status_code == 302

    editor_assignment = EditorAssignment.objects.get(article=article)
    article.refresh_from_db()

    assert editor_assignment.editor == selected_editor
    assert article.stage == "Assigned"


@pytest.mark.django_db
@override_settings(
    WJS_ARTICLE_ASSIGNMENT_FUNCTIONS={
        None: "wjs.jcom_profile.events.assignment.default_assign_editors_to_articles",
    },
)
def test_default_special_issue_articles_are_assigned_to_editor_with_lowest_workload_among_special_issue_editors(
    admin,
    article,
    coauthors_setting,
    special_issue,
):
    client = Client()
    client.force_login(admin)
    lowest_workload = 1000
    selected_editor = None
    for editor in special_issue.editors.all():
        params = EditorAssignmentParameters.objects.create(
            editor=editor,
            journal=special_issue.journal,
            workload=random.randint(1, 10),
        )
        if params.workload < lowest_workload:
            selected_editor = params.editor
            lowest_workload = params.workload

    url = reverse("submit_review", args=(article.pk,))

    response = client.post(url, data={"next_step": "next_step"})
    assert response.status_code == 302

    editor_assignment = EditorAssignment.objects.get(article=article)
    article.refresh_from_db()

    assert editor_assignment.editor == selected_editor
    assert article.stage == "Assigned"
