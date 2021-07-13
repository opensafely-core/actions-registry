from django.db import models


class Action(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    type = models.CharField(max_length=50)
    pub_date = models.DateTimeField("date published")

    def __str__(self):
        return self.name
