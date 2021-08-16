from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    # An action's repo's organisation is not included in the URL, because for now we
    # only allow actions from a single organisation ("opensafely-actions") and a URL of
    # eg actions.opensafely.org/actions/opensafely-actions/safetab/ looks a bit silly.
    # If in future we support actions from multiple organisations, we will have to
    # change this.
    path("actions/<str:repo_name>/", views.action, name="action"),
    path("actions/<str:repo_name>/<str:tag>/", views.version, name="version"),
]
