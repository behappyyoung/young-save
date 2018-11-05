from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Profiles(models.Model):
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=200, null=True)
    profile_id = models.CharField(max_length=100, null=True)
    account_id = models.CharField(max_length=100, null=True)
    gene_version = models.CharField(max_length=10, null=False, default=1)
    pre_score = models.CharField(max_length=100, null=True)
    score = models.CharField(max_length=100, null=True)