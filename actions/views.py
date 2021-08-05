from django.shortcuts import get_object_or_404, redirect, render

from .models import Action


def index(request):
    actions_list = Action.objects.order_by("repo_name")
    return render(request, "actions/index.html", {"actions": actions_list})


def action(request, action_id):
    action = get_object_or_404(Action, pk=action_id)
    version = action.get_latest_version()
    return redirect(version)


def version(request, action_id, tag):
    action = get_object_or_404(Action, pk=action_id)
    version = get_object_or_404(action.versions, tag=tag)

    return render(
        request,
        "actions/version.html",
        {
            "about": action.about,
            "readme": version.readme,
            "tag": version.tag,
            "name": action.repo_name,
        },
    )
