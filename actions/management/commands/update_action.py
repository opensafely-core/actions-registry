import pycmarkgfm
from django.core.management.base import BaseCommand

from actions.github import GithubClient
from actions.models import Action


class Command(BaseCommand):
    help = "Updates the readme file and about description for an action saved in the database"

    def add_arguments(self, parser):
        parser.add_argument("action_name")

    def handle(self, action_name, **options):

        action = Action.objects.get(name=action_name)

        client = GithubClient()

        repo = client.get_repo(f"{action.org}/{action.repo_name}")

        # get about
        details = repo.get_repo_details()
        action.about = details["about"]

        # get contents
        contents = repo.get_contents(path="docs/README.md", ref="main")
        readme = contents.decoded_content
        html_readme = pycmarkgfm.gfm_to_html(readme)

        html_readme = html_readme.replace(
            "<h3>", '<h3 class="text-sm font-semibold text-gray-600"> '
        )
        html_readme = html_readme.replace(
            "<p>", '<p class="mt-1 text-sm text-gray-900"> '
        )
        html_readme = html_readme.replace("<h5>", '<h5 class="text-sm font-semibold"> ')
        html_readme = html_readme.replace("<ul>", '<div class="list-disc">')

        action.readme = html_readme

        action.save()
