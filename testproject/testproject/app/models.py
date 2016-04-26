try:
    from django.contrib.postgres.fields.jsonb import JSONField
except ImportError:
    from django.db.models import TextField as JSONField

from django.db import models


class TestModel(models.Model):

    foo = models.CharField(max_length=255)
    bar = models.IntegerField()
    baz = JSONField()
