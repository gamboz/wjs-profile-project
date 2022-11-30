"""My views. Looking for a way to "enrich" Janeway's `edit_profile`."""
from collections import namedtuple
from dataclasses import dataclass
from typing import Iterable

import pandas as pd
from core import files as core_files
from core import logic
from core import models as core_models
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db import IntegrityError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DetailView, TemplateView, UpdateView
from repository import models as preprint_models
from security.decorators import submission_authorised
from submission import decorators
from submission import forms as submission_forms
from submission import logic as submission_logic
from submission import models as submission_models
from utils import setting_handler
from utils.logger import get_logger

from wjs.jcom_profile.forms import (
    DirectorEditorAssignmentParametersForm,
    EditorKeywordFormset,
    UpdateAssignmentParametersForm,
)
from wjs.jcom_profile.models import (
    EditorAssignmentParameters,
    JCOMProfile,
    SpecialIssue,
)

from . import forms
from .utils import PATH_PARTS, save_file_to_special_issue

logger = get_logger(__name__)


@login_required
def edit_profile(request):
    """Edit profile view for wjs app."""
    user = JCOMProfile.objects.get(pk=request.user.id)
    form = forms.JCOMProfileForm(instance=user)
    # copied from core.views.py::edit_profile:358ss

    if request.POST:
        if "email" in request.POST:
            email_address = request.POST.get("email_address")
            try:
                validate_email(email_address)
                try:
                    logic.handle_email_change(request, email_address)
                    return redirect(reverse("website_index"))
                except IntegrityError:
                    messages.add_message(
                        request,
                        messages.WARNING,
                        "An account with that email address already exists.",
                    )
            except ValidationError:
                messages.add_message(
                    request,
                    messages.WARNING,
                    "Email address is not valid.",
                )

        elif "change_password" in request.POST:
            old_password = request.POST.get("current_password")
            new_pass_one = request.POST.get("new_password_one")
            new_pass_two = request.POST.get("new_password_two")

            if old_password and request.user.check_password(old_password):

                if new_pass_one == new_pass_two:
                    problems = request.user.password_policy_check(request, new_pass_one)
                    if not problems:
                        request.user.set_password(new_pass_one)
                        request.user.save()
                        messages.add_message(request, messages.SUCCESS, "Password updated.")
                    else:
                        [messages.add_message(request, messages.INFO, problem) for problem in problems]
                else:
                    messages.add_message(request, messages.WARNING, "Passwords do not match")

            else:
                messages.add_message(request, messages.WARNING, "Old password is not correct.")

        elif "edit_profile" in request.POST:
            form = forms.JCOMProfileForm(request.POST, request.FILES, instance=user)

            if form.is_valid():
                form.save()
                messages.add_message(request, messages.SUCCESS, "Profile updated.")
                return redirect(reverse("core_edit_profile"))

        elif "export" in request.POST:
            return logic.export_gdpr_user_profile(user)

    context = {"form": form, "user_to_edit": user}
    template = "core/accounts/edit_profile.html"
    return render(request, template, context)


# from src/core/views.py::register
def register(request):
    """
    Display a form for users to register with the journal.

    If the user is registering on a journal we give them
    the Author role.
    :param request: HttpRequest object
    :return: HttpResponse object
    """
    token, token_obj = request.GET.get("token", None), None
    if token:
        token_obj = get_object_or_404(core_models.OrcidToken, token=token)

    form = forms.JCOMRegistrationForm()

    if request.POST:
        form = forms.JCOMRegistrationForm(request.POST)

        password_policy_check = logic.password_policy_check(request)

        if password_policy_check:
            for policy_fail in password_policy_check:
                form.add_error("password_1", policy_fail)

        if form.is_valid():
            if token_obj:
                new_user = form.save(commit=False)
                new_user.orcid = token_obj.orcid
                new_user.save()
                token_obj.delete()
            else:
                new_user = form.save()

            if request.journal:
                new_user.add_account_role("author", request.journal)
            logic.send_confirmation_link(request, new_user)

            messages.add_message(
                request,
                messages.SUCCESS,
                "Your account has been created, please follow the"
                "instructions in the email that has been sent to you.",
            )
            return redirect(reverse("core_login"))

    template = "core/accounts/register.html"
    context = {
        "form": form,
    }

    return render(request, template, context)


def confirm_gdpr_acceptance(request, token):
    """Explicitly confirm GDPR acceptance for invited users.

    The token encodes base user information (name, surname and email)
    """
    template = "admin/core/account/gdpr_acceptance.html"

    # verify the account existence
    try:
        account = JCOMProfile.objects.get(invitation_token=token)
    except JCOMProfile.DoesNotExist:
        context = {"error": True}
        return render(request, template, context, status=404)

    context = {
        "first_name": account.first_name,
        "last_name": account.last_name,
        "form": forms.GDPRAcceptanceForm(),
    }
    if request.POST:
        form = forms.GDPRAcceptanceForm(request.POST)
        if form.is_valid():
            template = "admin/core/account/thankyou.html"
            # if the form is valid and the existing account does not have the GDPR policy accepted, it is updated
            if not account.gdpr_checkbox:
                account.is_active = True
                account.gdpr_checkbox = True
                account.invitation_token = ""
                account.save()
                context["activated"] = True
                # Generate a temporary token to set a brand-new password
                core_models.PasswordResetToken.objects.filter(account=account).update(expired=True)
                reset_token = core_models.PasswordResetToken.objects.create(account=account)
                reset_psw_url = request.build_absolute_uri(
                    reverse(
                        "core_reset_password",
                        kwargs={"token": reset_token.token},
                    ),
                )
                # Send email.
                # FIXME: Email setting should be handled using the janeway settings framework.
                # See https://gitlab.sissamedialab.it/wjs/wjs-profile-project/-/issues/4
                send_mail(
                    settings.RESET_PASSWORD_SUBJECT,
                    settings.RESET_PASSWORD_BODY.format(account.first_name, account.last_name, reset_psw_url),
                    settings.DEFAULT_FROM_EMAIL,
                    [account.email],
                )
        else:
            context["form"] = form

    return render(request, template, context)


class SpecialIssues(TemplateView):
    """Views used to link an article to a special issue during submission."""

    form_class = forms.SIForm
    template_name = "admin/submission/submit_si_chooser.html"

    def post(self, *args, **kwargs):
        """Set the choosen special issue and continue.

        The SI is associated to the Article via an ArticleWrapper,
        that is created if not already present.

        """
        article = get_object_or_404(submission_models.Article, pk=kwargs["article_id"])
        form = self.form_class(self.request.POST, instance=article.articlewrapper)
        if form.is_valid():
            article_wrapper = form.save()
            return redirect(
                reverse(
                    "submit_info_original",
                    kwargs={"article_id": article_wrapper.janeway_article.id},
                ),
            )
        context = {"form": form, "article": article}
        return render(
            self.request,
            template_name=self.template_name,
            context=context,
        )

    def get(self, *args, **kwargs):
        """Show a form to choose the special issue to which one is submitting."""
        # The following should be safe, since article_id is not part
        # of the query string but of the path
        article = get_object_or_404(submission_models.Article, pk=kwargs["article_id"])
        # TODO: this is a stub: SI should be linked to the journal
        if not SpecialIssue.objects.current_journal().open_for_submission().exists():
            return redirect(
                reverse(
                    "submit_info_original",
                    kwargs={"article_id": kwargs["article_id"]},
                ),
            )
        form = self.form_class(instance=article.articlewrapper)

        # NB: templates (base and timeline and all) expect to find
        # "article" in context!
        context = {"form": form, "article": article}
        return render(
            self.request,
            template_name=self.template_name,
            context=context,
        )


@login_required
@decorators.submission_is_enabled
@submission_authorised
def start(request, type=None):  # NOQA
    """Start the submission process."""
    # TODO: See submission.views.start
    #  This view should be added to janeway core, avoiding useless code duplication.
    #  Expected behaviour: check user_automatically_author and user_automatically_main_author settings to eventually
    #  add article main author automatically.
    form = submission_forms.ArticleStart(journal=request.journal)

    if not request.user.is_author(request):
        request.user.add_account_role("author", request.journal)

    if request.POST:
        form = submission_forms.ArticleStart(request.POST, journal=request.journal)

        if form.is_valid():
            new_article = form.save(commit=False)
            new_article.owner = request.user
            new_article.journal = request.journal
            new_article.current_step = 1
            new_article.article_agreement = submission_logic.get_agreement_text(request.journal)
            new_article.save()

            if type == "preprint":
                preprint_models.Preprint.objects.create(article=new_article)

            user_automatically_author = setting_handler.get_setting(
                "general",
                "user_automatically_author",
                request.journal,
            ).processed_value
            user_automatically_main_author = setting_handler.get_setting(
                "general",
                "user_automatically_main_author",
                request.journal,
            ).processed_value

            if user_automatically_author:
                submission_logic.add_user_as_author(request.user, new_article)
                if user_automatically_main_author:
                    new_article.correspondence_author = request.user
                new_article.save()

            return redirect(reverse("submit_info", kwargs={"article_id": new_article.pk}))

    template = "admin/submission/start.html"
    context = {"form": form}

    return render(request, template, context)


class SICreate(PermissionRequiredMixin, CreateView):
    """Create a Special Issue."""

    permission_required = "jcom_profile.add_specialissue"
    # see also security.decorators.editor_or_manager

    model = SpecialIssue
    fields = ["name", "short_name", "description", "open_date", "close_date", "journal"]


class SIDetails(DetailView):
    """View a Special Issue."""

    model = SpecialIssue


class SIUpdate(PermissionRequiredMixin, UpdateView):
    """Update a Special Issue."""

    # "add" and "update" operations share the same permissions
    permission_required = "jcom_profile.add_specialissue"

    model = SpecialIssue
    # same fields as SICreate; do not add "documents": they are dealt with "manually"
    fields = ["name", "short_name", "description", "open_date", "close_date", "journal"]


# Adapted from journal.views.serve_article_file
# TODO: check and ri-apply authorization logic
# @has_request
# @article_stage_accepted_or_later_or_staff_required
# @file_user_required
def serve_special_issue_file(request, special_issue_id, file_id):
    """Serve a special issue file.

    :param request: the request associated with this call
    :param special_issue_id: the identifier for the special_issue
    :param file_id: the file ID to serve
    :return: a streaming response of the requested file or 404
    """
    if file_id != "None":
        file_object = get_object_or_404(core_models.File, pk=file_id)
        # Ugly: sneakily introduce the special issue's ID in the file path
        mangled_parts = [
            *PATH_PARTS,
            str(special_issue_id),
        ]
        return core_files.serve_any_file(
            request,
            file_object,
            path_parts=mangled_parts,
        )
    else:
        raise Http404


class SIFileUpload(View):
    """Upload a special issue document."""

    def post(self, request, special_issue_id):
        """Upload the given file and redirect to update view."""
        si = get_object_or_404(SpecialIssue, pk=special_issue_id)
        new_file = request.FILES.get("new-file")
        saved_file = save_file_to_special_issue(new_file, si, request.user)
        si.documents.add(saved_file)
        return redirect(reverse("si-update", args=(special_issue_id,)))


class SIFileDelete(PermissionRequiredMixin, View):
    """Delete a special issue document."""

    permission_required = "core.delete_file"

    def post(self, request, file_id):
        """Delete the given file and redirect.

        Expect a query parameter named `return` in the `request`. It
        is used at the redirect URL.

        """
        file_obj = get_object_or_404(core_models.File, pk=file_id)
        file_obj.delete()
        return redirect(request.GET["return"])


class EditorAssignmentParametersUpdate(UserPassesTestMixin, UpdateView):
    """Change editor's own submission parameters."""

    model = EditorAssignmentParameters
    form_class = UpdateAssignmentParametersForm
    template_name = "submission/update_editor_parameters.html"
    raise_exception = True

    def test_func(self):  # noqa
        user = self.request.user
        journal = self.request.journal
        return user.check_role(
            journal,
            "editor",
        )

    def get_object(self, queryset=None):  # noqa
        editor, journal = self.request.user, self.request.journal
        parameters, _ = EditorAssignmentParameters.objects.get_or_create(editor=editor, journal=journal)
        return parameters

    def get_success_url(self):  # noqa
        messages.add_message(
            self.request,
            messages.SUCCESS,
            "Parameters updated successfully",
        )
        return reverse("assignment_parameters")


class DirectorEditorAssignmentParametersUpdate(UserPassesTestMixin, UpdateView):
    """Change editors parameters as journal director.

    Use formsets to update EditorKeyword instances weights.

    """

    model = EditorAssignmentParameters
    form_class = DirectorEditorAssignmentParametersForm
    template_name = "submission/director_update_editor_parameters.html"
    raise_exception = True

    def test_func(self):  # noqa
        user = self.request.user
        return user.is_staff

    def get_object(self, queryset=None):  # noqa
        editor_pk, journal = self.kwargs.get("editor_pk"), self.request.journal
        editor = JCOMProfile.objects.get(pk=editor_pk)
        if not editor.check_role(journal, "editor"):
            raise Http404()
        parameters, _ = EditorAssignmentParameters.objects.get_or_create(editor=editor, journal=journal)
        return parameters

    def get_context_data(self, **kwargs):  # noqa
        context = super().get_context_data()
        if self.request.POST:
            formset = EditorKeywordFormset(data=self.request.POST, instance=self.object)
            formset.is_valid()
        else:
            formset = EditorKeywordFormset(instance=self.object)
        context["formset"] = formset
        return context

    def form_valid(self, form):  # noqa
        context = self.get_context_data()
        formset = context.get("formset")
        if formset.is_valid():
            formset.save()
        else:
            return self.render_to_response(self.get_context_data())
        return super().form_valid(form)

    def get_success_url(self):  # noqa
        messages.add_message(
            self.request,
            messages.SUCCESS,
            "Parameters updated successfully",
        )
        return reverse("assignment_parameters", args=(self.kwargs.get("editor_pk"),))


@dataclass
class PartitionLine:
    """A line representing a collection partition.

    Or the section of a conference.
    """

    name: str

    def __init__(self, line):
        """Take an odt line and make into a PartitionLine."""
        self.name = line.colums[0]


@dataclass
class SuggestionLine:
    """A create / merge / merge+edit / ignore suggestion."""

    suggestion_type: str
    first: str
    middle: str
    last: str
    email: str  # TODO: use some kind of email type like Type(email_address)
    affiliation: str
    title: str
    pk: int


@dataclass
class ContributionLine:
    """A line representing a contribution.

    Here we also keep "suggestions" of similar authors from the database.
    """

    first: str
    middle: str
    last: str
    email: str  # TODO: use some kind of email type like Type(email_address)
    affiliation: str
    title: str
    suggestions: Iterable[SuggestionLine]

    def __init__(self, row: namedtuple):
        """Build a ContributionLine from a Pandas namedtuple."""
        # TODO: map me more elegantly: can I unpack the namedtuple
        # directly into the default __init__ of the dataclass?
        self.first = row.first
        self.middle = row.middle
        self.last = row.last
        self.email = row.email
        self.affiliation = row.affiliation
        self.title = row.title


class IMUStep1(TemplateView):
    """Insert Many Users - first step.

    Manage the data file upload form.
    """

    form_class = forms.IMUForm

    def get(self, *args, **kwargs):
        """Show a form to start the IMU process - upload the data file."""
        form = self.form_class()
        return render(
            self.request,
            template_name=self.template_name,
            context={"form": form},
        )

    def post(self, *args, **kwargs):
        """Receive the data file, process it and redirect along to the next step."""
        form = self.form_class(self.request.POST, self.request.FILES)
        if not form.is_valid:
            return render(
                self.request,
                template_name=self.template_name,
                context={"form": form},
            )
        data_file = form.files["data_file"]
        context = {"lines": self.process_data_file(data_file)}
        return render(
            self.request,
            template_name="admin/core/si_imu_check.html",
            context=context,
        )

    def process_data_file(self, data_file) -> Iterable[ContributionLine]:
        """Prepare data file to be presented in the input/merge form."""
        result_lines = []

        columns_names = ("first", "middle", "last", "email", "affiliation", "title")
        sheet_index = 0
        df = pd.read_excel(
            data_file.read(),
            sheet_name=sheet_index,
            header=None,
            names=columns_names,
            engine="odf",
        )
        # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.itertuples.html#pandas.DataFrame.itertuples
        for row in df.itertuples(index=False):
            line = self.examine_row(row)
            result_lines.append(line)

    def examine_row(self, row: namedtuple) -> ContributionLine:
        """Parse a odt row (pandas namedtuple) into a Line.

        Line can be a PartitionLine or a ContributionLine with its suggestions.
        """
        # Allow for dirty data: if I'm missing lastname and email,
        # I'll consider this a PartitionLine and just use the
        # firstname column as the partition name.
        if not row.last and not row.email:
            return PartitionLine(name=row.first)
        line = ContributionLine(row)
        line.suggestions = self.make_suggestion(line)
        return line

    def save_to_tmp(self, infile: UploadedFile) -> None:
        """Save the given uploaded file to a temporary file.

        Used to pass a path to pandas' `read_ods`.
        """
        path = f"/tmp/{infile.name}"
        with open(path, "wb+") as destination:
            for chunk in infile.chunks():
                destination.write(chunk)
        return path

    def author_p(self, line):
        """Take an odt line and check if it is valid "contribution line".

        Basically just count the columns.
        Also, fill all missing columns with None.
        """
        expected_column_count = 5
        for i in range(expected_column_count):
            if i > line.column_count:
                line.add_column(None)

    def make_suggestion(self, line: ContributionLine) -> Iterable[SuggestionLine]:
        """Take a contribution line and find similar users in the DB."""
        suggestions = []
        try:
            # Find similar users in the DB by email
            # expect at most one and when one is found that is sufficient
            suggestions.append(core_models.Account.objects.get(email=line.email))
        except core_models.Account.DoesNotExist:
            suggestions = self.make_more_suggestions(line)
        return suggestions

    def make_more_suggestions(self, line: ContributionLine) -> Iterable[SuggestionLine]:
        """Take a contribution line and find similar users in the DB by euristics."""
        suggestions = []
        suggestions.append(
            core_models.Account.objects.filter(
                last_name=line.last,
                first_name__istartswith=f"{line.first[0]}%",
            ),
        )
        return suggestions
