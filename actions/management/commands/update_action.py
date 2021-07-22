from django.core.management.base import BaseCommand
from django.db import transaction

from actions.github import GithubClient
from actions.models import Action, Version


class Command(BaseCommand):
    help = "Updates the readme file and about description for an action saved in the database"

    def add_arguments(self, parser):
        parser.add_argument("action_name")

    @transaction.atomic
    def handle(self, action_name, **options):

        action = Action.objects.get(name=action_name)

        client = GithubClient()
        repo = client.get_repo(f"{action.org}/{action.repo_name}")

        # get about
        details = repo.get_repo_details()
        action.about = details["about"]
        action.save()

        # get all tags for repo
        tags = repo.get_tags()

        # loop through all tags and add to db with api calls for readme
        for tag in tags:
            readme = repo.get_readme(tag=tag["tag_name"])
            tag_details = repo.get_commit(sha=tag["sha"])

            Version.objects.get_or_create(
                action=action,
                tag=tag["tag_name"],
                date=tag_details["date"],
                readme=readme,
            )
