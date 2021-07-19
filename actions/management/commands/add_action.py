import pycmarkgfm
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
        html_readme = pycmarkgfm.gfm_to_html(readme)

        html_readme = html_readme.replace(
            "<h3>", '<h3 class="text-sm font-semibold text-gray-600"> '
        )
        html_readme = html_readme.replace(
            "<p>", '<p class="mt-1 text-sm text-gray-900"> '
        )
        html_readme = html_readme.replace("<h5>", '<h5 class="text-sm font-semibold"> ')
        html_readme = html_readme.replace("<ul>", '<div class="list-disc">')

        action = Action(
            name=details["name"],
            org=org,
            repo_name=repo_name,
            readme=html_readme,
            about=details["about"],
        )

        action.save()
