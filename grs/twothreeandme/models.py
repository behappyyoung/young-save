from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
from django_mysql.models import JSONField, Model


class Positions(models.Model):
    name = models.CharField(max_length=200, null=True)
    positions = models.CharField(max_length=200, null=True)


class ResponseLog(models.Model):
    request_time = models.DateTimeField(auto_now=True)
    action = models.CharField(max_length=100, null=True)
    request_header = models.CharField(max_length=200, null=True)
    url = models.CharField(max_length=200, null=True)
    response = models.TextField(null=True)


class Patients(models.Model):
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=200, null=True)
    profile_id = models.CharField(max_length=100, null=True)
    account_id = models.CharField(max_length=100, null=True)
    gene_version = models.CharField(max_length=10, null=False, default=1)
    pre_score = models.CharField(max_length=100, null=True)
    score = models.CharField(max_length=100, null=True)


class Accessions(models.Model):
    cid = models.CharField(max_length=5, null=True)
    aid = models.CharField(max_length=20, null=False)
    start_pos = models.CharField(max_length=20, null=True)
    end_pos = models.CharField(max_length=20, null=True)
    allele_1 = models.CharField(max_length=200, null=True)
    allele_2 = models.CharField(max_length=200, null=True)
    platform_labels = models.CharField(max_length=500, null=True)


class Chromosome(models.Model):
    url = models.CharField(max_length=300, null=True)
    cid = models.CharField(max_length=5, null=True)
    offset = models.CharField(max_length=20, null=True)
    data = models.TextField(null=True)
    links = models.CharField(max_length=300, null=True)
    models.DateTimeField(null=True, default=timezone.now)


class GenotypesV1(models.Model):
    patient = models.ForeignKey('Patients', on_delete=models.CASCADE, null=False)
    file_name = models.CharField(max_length=100, null=True)
    alleles = JSONField(null=True)
    result_json = JSONField(null=True)
    data_text = models.TextField(null=True)


class Genotypes(models.Model):
    patient = models.ForeignKey('Patients', on_delete=models.CASCADE, null=False)
    aid = models.ForeignKey('Accessions', on_delete=models.CASCADE, null=True)
    allele1 = models.CharField(max_length=5, null=False, default='-')
    allele2 = models.CharField(max_length=5, null=False, default='-')
    genotyped = models.BooleanField(null=False, default=True)
    no_calls = models.BooleanField(null=False, default=True)


class GenomeSnpMap(models.Model):
    ttm_index = models.CharField(max_length=10, null=False)
    ref = models.CharField(max_length=200, null=False)
    chromosome = models.CharField(max_length=10, null=False)
    position = models.CharField(max_length=20, null=False)
