from django.db import models


class Action(models.Model):
    name = models.CharField(max_length=200)
    org = models.CharField(max_length=200)
    repo_name = models.CharField(max_length=200)
    about = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ["org", "repo_name"]


class Version(models.Model):
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    tag = models.CharField(max_length=100)
    date = models.DateField()
    readme = models.TextField()

    def __str__(self):
        return f"{self.action} - {self.tag}"

    class Meta:
        unique_together = ["action", "tag"]  # might be action_id
