from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from osgithub import GithubAPIException, GithubClient

from ...models import Action


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("organisation")
        parser.add_argument("repo_name")

    @transaction.atomic
    def handle(self, organisation, repo_name, **options):
        if organisation not in settings.ALLOWED_ORGS:
            raise CommandError(
                "This repo belongs to an organisation outside our allowed list."
            )

        client = GithubClient()

        try:
            repo = client.get_repo(organisation, repo_name)
        except GithubAPIException as e:
            if str(e) == "Not Found":
                raise CommandError("Repo not found")
            raise  # pragma: no cover

        details = repo.get_repo_details()
        tags = repo.get_tags()
        action, created = Action.objects.update_or_create(
            repo_name=repo_name,
            org=organisation,
            defaults={
                "about": str(details["about"] or ""),
            },
        )

        for tag in tags:
            readme = repo.get_readme(tag=tag["tag_name"])
            tag_details = repo.get_commit(sha=tag["sha"])

            action.versions.update_or_create(
                tag=tag["tag_name"],
                defaults={
                    "committed_at": tag_details["date"],
                    "readme": readme,
                },
            )

        if created:
            self.stdout.write("Created new Action")
        else:
            self.stdout.write("Updated existing Action")
