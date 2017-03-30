from __future__ import unicode_literals
from django.db import connection
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User


class CustomSQL:
    def my_custom_sql(self, sql):
        cursor = connection.cursor()
        cursor.execute(sql)
        fieldnames = [name[0] for name in cursor.description]
        result = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            result.append(dict(rowset))
        return result


class CustomSql:
    def __init__(self):
        self.cursor = connection.cursor()

    def custom_sql(self, sql):
        self.cursor.execute(sql)
        fieldnames = [name[0] for name in self.cursor.description]
        result = []
        for row in self.cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            result.append(dict(rowset))
        return result


MESSAGE_TYPE = (
    ('text', 'text'), ('file', 'file'), ('html', 'html text')
)


class MiscMessage(models.Model):
    title = models.CharField(max_length=200, default='..')
    type = models.CharField(max_length=200, choices=MESSAGE_TYPE, default='text')
    content = models.CharField(max_length=200, default='..')
    date = models.DateTimeField(default=datetime.now)


class SaveTempdata(models.Model):
    type = models.CharField(max_length=200, default='json')
    name = models.CharField(max_length=200, default='..')
    date = models.DateTimeField(default=datetime.now)
    data = models.CharField(max_length=2000, default='[]')


LISTS_TYPES = (('title', 'group title'), ('check', 'boolean'), ('text', 'text'))


class PhenoTypeListsTypes(models.Model):
    name = models.CharField(max_length=200, default='text')
    desc = models.CharField(max_length=200, default='..')

    def __unicode__(self):
        return self.name


class PhenoTypeCategory(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False, default='..')
    display_name = models.CharField(max_length=200, default='..')
    priority = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name


class HistoryCategory(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False, default='..')
    display_name = models.CharField(max_length=200, default='..')
    priority = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name


class GeneCategory(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False, default='..')
    display_name = models.CharField(max_length=200, default='..')
    priority = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name


class InputTypes(models.Model):
    name = models.CharField(max_length=200, default='text')
    desc = models.CharField(max_length=200, default='..')

    def __unicode__(self):
        return self.name


class PhenoTypeLists(models.Model):
    category = models.ForeignKey(PhenoTypeCategory, related_name="pheno_categroy", on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=200, default='..')
    type = models.ForeignKey(InputTypes, related_name="pheno_type", on_delete=models.CASCADE, default=1)
    desc = models.CharField(max_length=200, default='..')
    priority = models.IntegerField(default=0)


class HistoryLists(models.Model):
    category = models.ForeignKey(HistoryCategory, related_name="history_category", on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=200, default='..')
    type = models.ForeignKey(InputTypes, related_name="history_type", on_delete=models.CASCADE, default=1)
    desc = models.CharField(max_length=200, default='..')
    priority = models.IntegerField(default=0)


class GeneLists(models.Model):
    category = models.ForeignKey(GeneCategory, related_name="gene_categroy", on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=50, default='..')
    list = models.TextField(default='..')
    desc = models.CharField(max_length=200, default='..')
    priority = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name


class GCloudFiles(models.Model):
    name = models.CharField(max_length=50, default='')
    obj_type = models.CharField(max_length=50, default='')
    obj_id = models.CharField(max_length=50, default='')
    file_type = models.CharField(max_length=50, default='')
    file_path = models.CharField(max_length=100, default='')        # file path after file_root /
    url = models.CharField(max_length=200, null=True, default='')
    upload_date = models.CharField(max_length=50, null=False, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    upload_by = models.ForeignKey(User, related_name='upload_by', blank=True, null=True, default='')

    def __unicode__(self):
        return self.name
