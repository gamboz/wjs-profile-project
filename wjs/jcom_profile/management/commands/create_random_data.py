"""Populate a journal with random demostrative data."""

from datetime import timedelta

import factory
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker.providers import lorem
from journal.models import Journal
from submission import models as submission_models
from submission.models import STAGE_PUBLISHED, Article

from wjs.jcom_profile.models import JCOMProfile

factory.Faker.add_provider(lorem)

# TODO: move factories to some generic utility module

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
    # By default, link this article to the first journal
    # (I think this breaks if there are no journal, but how whould one
    # create articles in that case anyway 🙂)
    journal = factory.Iterator((Journal.objects.first(),))
    # Link to random article type / section
    section = factory.Iterator(submission_models.Section.objects.all())
    # TODO: use dall.e (https://labs.openai.com) to fill `thumbnail_image_file`


class Command(BaseCommand):
    help = "Create a user and an article for the first journal in the press."  # NOQA

    def handle(self, *args, **options):
        """Command entry point."""
        user = self._create_user(**options)
        self._create_article(user, **options)

    def add_arguments(self, parser):
        """Add arguments to command."""
        parser.add_argument("--roles", help='Roles, as a comma-separated string (e.g. "editor,reader").')

    def _create_user(self, **options):
        """Create a user, honoring roles."""
        user = UserFactory.create()
        self.stdout.write(self.style.SUCCESS(f"Creating {user}..."))
        user.save()

        # Always add the role "author" because we'll use this user as
        # author of an article:
        journal = Journal.objects.get(pk=1)
        user.add_account_role("author", journal)

        roles = options["roles"]
        if roles:
            for role_slug in roles.split(","):
                self.stdout.write(self.style.SUCCESS(f"  adding role {role_slug}"))
                user.add_account_role(role_slug, journal)
        user.save()
        self.stdout.write(self.style.SUCCESS("  ...done"))
        return user

    def _create_article(self, user, **options):
        """Create an article on the first journal, set the user as author."""
        article = ArticleFactory.create()
        self.stdout.write(self.style.SUCCESS(f"Creating {article}"))
        article.save()
        article.owner = user
        article.authors = [user]
        article.correspondence_author = user
        # publish article
        # see src/journal/views.py:1078
        article.stage = STAGE_PUBLISHED
        article.snapshot_authors()
        article.close_core_workflow_objects()
        article.date_published = timezone.now() - timedelta(days=1)
        article.save()
        self.stdout.write(self.style.SUCCESS("  ...done"))
