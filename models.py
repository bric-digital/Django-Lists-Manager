# pylint: disable=line-too-long

from django.contrib.postgres.fields import ArrayField
from django.db import models

class Vocabulary(models.Model):
    name = models.CharField(max_length=1024)

    definition = models.JSONField(null=True, blank=True)

    def __str__(self):
        return '%s' % self.name

class List(models.Model):
    name = models.CharField(max_length=1024)
    description = models.TextField(max_length=(1024 * 1024), null=True, blank=True)

    vocabulary = models.ForeignKey(Vocabulary, related_name='lists', blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return '%s' % self.name

class ListItem(models.Model):
    name = models.CharField(max_length=1024)

    member_of = models.ForeignKey(List, related_name='members', on_delete=models.CASCADE)

    value = models.CharField(max_length=1024)

    item_type = models.CharField(max_length=1024, null=True, blank=True, db_index=True)

    tags = ArrayField(models.CharField(max_length=64), blank=True, null=True)

    def __str__(self):
        return '%s (%s)' % (self.name, self.member_of)
