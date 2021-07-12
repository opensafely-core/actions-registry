from django.http import HttpResponse, Http404
from django.template import loader
from django.shortcuts import render, get_object_or_404

from .models import Actions


# Create your views here.
def index(request):
    actions_list = Actions.objects.order_by('pub_date')
    template = loader.get_template('actions/index.html')
    context = {
        'actions_list': actions_list
        }
    return HttpResponse(template.render(context, request))


def detail(request, action_id):
    action = get_object_or_404(Actions, pk=action_id)
    return render(request, 'actions/detail.html', {'action': action})
