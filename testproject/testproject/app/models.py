from django.contrib.postgres.fields import JSONField
from django.db import models


class TestModel(models.Model):

    foo = models.CharField(max_length=255)
    bar = models.IntegerField()
    baz = JSONField()
