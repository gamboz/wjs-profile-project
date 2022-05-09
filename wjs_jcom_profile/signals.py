"""Signals.

Every time a user model instance is created, a corresponding JCOM
profile instance must be created as well.

"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from wjs_jcom_profile.models import JCOMProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_handler(sender, instance, created, **kwargs):
    """Create the JCOM profile, only if the Account is newly created."""
    if not created:
        return

    # TODO: move defalt to model OR
    # change the user-creation form OR
    # do something else?
    default_profession = 3
    # import ipdb; ipdb.set_trace()

    JCOMProfile.objects.create(
        janeway_account=instance,
        profession=default_profession)

    # If I don't `save()` the instance also, an empty record is
    # created.
    #
    # I think this is because the post_save message is emitted by one
    # of core.forms.RegistrationForm's ancestor (l.133) but with
    # `commit=False`, so that the form's data is not yet in the DB.
    instance.save()
    # TODO: tests instance.save_m2m()
    # https://django.readthedocs.io/en/stable/topics/forms/modelforms.html?highlight=save_m2m#the-save-method
