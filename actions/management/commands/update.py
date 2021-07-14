from django.core.management.base import BaseCommand

from actions.github import GithubClient
from actions.models import Action


class Command(BaseCommand):
    help = "Updates the readme file for an action saved in the database"

    def add_arguments(self, parser):
        parser.add_argument("action_name")

    def handle(self, *args, **options):

        action = Action.objects.get(name=options["action_name"])

        client = GithubClient()

        repo = client.get_repo(f"{action.org}/{action.repo_name}")

        # get contents
        contents = repo.get_contents(path="docs/README.md", ref="main")
        readme = contents.decoded_content

        action.readme = readme
        action.save()
