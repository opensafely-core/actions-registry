from django.db import models


class Action(models.Model):
    name = models.CharField(max_length=200)
    org = models.CharField(max_length=200)
    repo_name = models.CharField(max_length=200)
    readme = models.CharField(max_length=2000)
    about = models.CharField(max_length=400)

    def __str__(self):
        return self.name
