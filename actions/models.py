from django.db import models
from django.urls import reverse


class Action(models.Model):
    org = models.CharField(max_length=200)
    repo_name = models.CharField(max_length=200)
    about = models.TextField()

    def __str__(self):
        return self.repo_name

    class Meta:
        unique_together = ["org", "repo_name"]

    def get_latest_version(self):
        """Return version with latest committed_at."""

        latest_version = Version.objects.filter(action=self.id).latest("committed_at")
        return latest_version

    def get_absolute_url(self):
        """Return canonical URL for this Action."""

        return reverse("action", kwargs={"repo_name": self.repo_name})

    def get_github_url(self):
        """Return URL of this Action's repo in GitHub."""

        return f"https://github.com/{self.org}/{self.repo_name}/"


class Version(models.Model):
    action = models.ForeignKey(
        Action, related_name="versions", on_delete=models.CASCADE
    )
    tag = models.CharField(max_length=100)
    committed_at = models.DateTimeField()
    readme = models.TextField()

    def __str__(self):
        return f"{self.action.repo_name} - {self.tag}"

    class Meta:
        unique_together = ["action", "tag"]

    def get_absolute_url(self):
        """Return canonical URL for this Version."""

        return reverse(
            "version",
            kwargs={"repo_name": self.action.repo_name, "tag": self.tag},
        )
