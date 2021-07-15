from django.core.management.base import BaseCommand

from actions.github import GithubClient
from actions.models import Action


class Command(BaseCommand):
    help = "Grabs the data from the actions repos and saves into database"

    def add_arguments(self, parser):
        parser.add_argument("action_url")

    def handle(self, action_url, **options):

        client = GithubClient()

        repo = client.get_repo(action_url)

        # get details
        details = repo.get_repo_details()

        org, repo_name = action_url.split("/")

        # get contents
        contents = repo.get_contents(path="docs/README.md", ref="main")
        readme = contents.decoded_content

        action = Action(
            name=details["name"],
            org=org,
            repo_name=repo_name,
            readme=readme,
            about=details["about"],
        )

        action.save()
