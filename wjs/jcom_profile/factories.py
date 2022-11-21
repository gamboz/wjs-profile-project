"""Utility factories.

Used in management commands and tests.
"""
import factory
from faker.providers import lorem
from journal.models import Journal
from submission import models as submission_models
from submission.models import Article

from wjs.jcom_profile.models import JCOMProfile

factory.Faker.add_provider(lorem)

# Not using model-baker because I could find a way to define a fake field
# that depend on another one (since in J. username == email). E.g.:
# Recipe("core.Account", ...  email=fake.email(),  username=email, ⇒ ERROR!


class UserFactory(factory.django.DjangoModelFactory):
    """User factory."""

    class Meta:
        model = JCOMProfile  # ← is this correct? maybe core.Account?

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    username = email
    is_admin = False
    is_active = True


class ArticleFactory(factory.django.DjangoModelFactory):
    """Article factory."""

    class Meta:
        model = Article

    title = factory.Faker("sentence", nb_words=7)
    abstract = factory.Faker("paragraph", nb_sentences=5)
    # By default, link this article to a random journal
    # (I think this breaks if there are no journal, but how whould one
    # create articles in that case anyway 🙂)
    # NB, these give error when used by pytest (not marked for db access):
    # - journal = factory.Iterator((Journal.objects.first(),))
    # - journal = Journal.objects.first()
    journal = factory.Iterator(Journal.objects.all())
    # Link to random article type / section
    section = factory.Iterator(submission_models.Section.objects.all())
    # TODO: use dall.e (https://labs.openai.com) to fill `thumbnail_image_file`
