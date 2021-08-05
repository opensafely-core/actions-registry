from django.urls import path

from . import views


app_name = "actions"
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:action_id>/", views.action, name="action"),
    path("<int:action_id>/<str:tag>/", views.version, name="version"),
]
