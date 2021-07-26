from django.core.exceptions import PermissionDenied
from django.core.management.base import BaseCommand
from django.db import transaction

from actions.github import GithubClient
from actions.models import Action, Version

ALLOWED_ORGS = ["opensafely-actions"]


class Command(BaseCommand):
    help = "Grabs the data from the actions repos and saves into database"

    def add_arguments(self, parser):
        parser.add_argument("action_url")

    @transaction.atomic
    def handle(self, action_url, **options):

        client = GithubClient()
        repo = client.get_repo(action_url)
        org, repo_name = action_url.split("/")

        if org not in ALLOWED_ORGS:
            raise PermissionDenied(
                "This Action belongs to an organisation outside our allowed list."
            )

        # get details - same for all tags
        details = repo.get_repo_details()
        action = Action(
            name=details["name"],
            org=org,
            repo_name=repo_name,
            about=details["about"],
        )
        action.save()

        # get all tags for repo
        tags = repo.get_tags()

        # loop through all tags and add to db with api calls for readme
        for tag in tags:
            readme = repo.get_readme(tag=tag["tag_name"])
            tag_details = repo.get_commit(sha=tag["sha"])

            version = Version(
                action=action,
                tag=tag["tag_name"],
                date=tag_details["date"],
                readme=readme,
            )
            version.save()
