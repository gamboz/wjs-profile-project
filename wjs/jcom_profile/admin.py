"""Register the models with the admin interface."""
import base64
import json

from django.contrib import admin, messages

from wjs.jcom_profile import forms, models
from wjs.jcom_profile.models import JCOMProfile
# from django.contrib.admin.sites import NotRegistered
from django.conf import settings
from core.models import Account
from core.admin import AccountAdmin

from django.conf.urls import url
from django.core.mail import send_mail
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse


class JCOMProfileInline(admin.StackedInline):
    """Helper class to "inline" account profession."""

    model = JCOMProfile
    fields = ['profession', 'gdpr_checkbox', 'invitation_token']
    # TODO: No! this repeats all the fields (first name, password,...)


# TODO: use settings.AUTH_USER_MODEL
# from django.conf import settings
class UserAdmin(AccountAdmin):
    """Another layer..."""

    inlines = (JCOMProfileInline,)

    def get_urls(self):
        urls = super().get_urls()
        import_users_url = [
            url("invite/", self.admin_site.admin_view(self.invite), name="invite")
        ]
        return import_users_url + urls

    def invite(self, request):
        if request.method == 'POST':
            form = forms.InviteUserForm(request.POST)
            if form.is_valid():
                data = base64.urlsafe_b64encode(
                    json.dumps(
                        {k: item for k, item in form.data.items() if k != "csrfmiddlewaretoken"}).encode()).decode()
                models.JCOMProfile.objects.create(
                    email=form.data["email"],
                    first_name=form.data["first_name"],
                    last_name=form.data["last_name"],
                    department=form.data["department"],
                    institution=form.data["institution"],
                    invitation_token=data,
                    is_active=False
                )
                url = reverse("accept_gdpr", kwargs={"token": data})
                mail_text = f"{form.data['plain_text']} \n {url}"
                send_mail(
                    "Join JCOM journal",
                    mail_text,
                    settings.DEFAULT_FROM_EMAIL,
                    [form.data["email"]]
                )
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'Account created',
                )
                return HttpResponseRedirect(reverse("admin:core_account_changelist"))

        template = "admin/core/account/invite.html"
        context = {
            "form": forms.InviteUserForm(),
        }
        return render(request, template, context)


admin.site.unregister(Account)
admin.site.register(Account, UserAdmin)
