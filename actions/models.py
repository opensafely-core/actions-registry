from django.db import models


class Action(models.Model):
    name = models.CharField(max_length=200)
    org = models.CharField(max_length=200)
    repo_name = models.CharField(max_length=200)
    readme = models.TextField()
    about = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ["org", "repo_name"]
