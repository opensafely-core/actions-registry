from django.db import models


# Create your models here.
class Actions(models.Model):
    action_name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    type_of_action = models.CharField(max_length=50)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.action_name
