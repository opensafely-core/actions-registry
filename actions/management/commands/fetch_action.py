import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from osgithub import GithubAPIException, GithubClient

from ...models import Action


class Command(BaseCommand):
    actions = [
        "opensafely-actions/cohort-joiner",
        "opensafely-actions/cohort-report",
        "opensafely-actions/cox-ipw",
        "opensafely-actions/dataset-report",
        "opensafely-actions/deciles-charts",
        "opensafely-actions/demographic-standardisation",
        "opensafely-actions/diabetes-algo",
        "opensafely-actions/kaplan-meier-function",
        "opensafely-actions/project-dag",
        "opensafely-actions/safetab",
    ]

    def handle(self, *args, **kwargs):
        for action in self.actions:
            organisation, repo_name = action.split("/")
            self.fetch_action(organisation, repo_name)

    @transaction.atomic
    def fetch_action(self, organisation, repo_name, **options):
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
        contributors = [i for i in repo.get_contributors() if "[bot]" not in i]
        tags = repo.get_tags()
        action, created = Action.objects.update_or_create(
            repo_name=repo_name,
            org=organisation,
            defaults={
                "about": str(details["about"] or ""),
                "contributors": contributors,
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
            sys.stdout.write(f"Created {organisation}/{repo_name}\n")
        else:
            sys.stdout.write(f"Updated {organisation}/{repo_name}\n")
