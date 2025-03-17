from urllib.parse import urljoin

from django.shortcuts import get_object_or_404, redirect, render

from actions.utils import resolve_relative_urls_to_absolute

from .models import Action


def index(request):
    actions_list = Action.objects.order_by("repo_name")
    return render(request, "actions/index.html", {"actions": actions_list})


def action(request, repo_name):
    action = get_object_or_404(Action, repo_name=repo_name)
    version = action.get_latest_version()
    return redirect(version)


def version(request, repo_name, tag):
    action = get_object_or_404(Action, repo_name=repo_name)
    version = get_object_or_404(action.versions, tag=tag)

    readme = resolve_relative_urls_to_absolute(
        version.readme,
        urljoin(action.get_github_url(), f"blob/{version.tag}/"),
        "href",
    )

    readme = resolve_relative_urls_to_absolute(
        readme,
        urljoin(action.get_github_url(), f"raw/{version.tag}/"),
        "src",
    )

    return render(
        request,
        "actions/version.html",
        {
            "action": action,
            "version": version,
            "readme": readme,
        },
    )
