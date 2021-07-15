from django.shortcuts import get_object_or_404, render

from .models import Action


def index(request):
    actions_list = Action.objects.order_by("name")
    return render(request, "actions/index.html", {"actions": actions_list})


def detail(request, action_id):
    action = get_object_or_404(Action, pk=action_id)
    return render(request, "actions/detail.html", {"action": action})
