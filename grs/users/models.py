from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# for user models


class UserGroup(models.Model):
    name = models.CharField(max_length=50, unique=True)


class UserRole(models.Model):
    name = models.CharField(max_length=50, unique=True)


# extending User Model with extra fields
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    title = models.CharField(max_length=200, null=True)
    username = models.CharField(max_length=100, null=True, default='')                      # name id - from S.A.M.L.
    session_index = models.CharField(max_length=100, null=True)
    group = models.CharField(max_length=50, default=' ')
    role = models.CharField(max_length=50, default=' ')
    widgetlist = models.CharField(max_length=200, null=True, blank=True)                  # save list as array for now

    def __unicode__(self):
        return self.username





