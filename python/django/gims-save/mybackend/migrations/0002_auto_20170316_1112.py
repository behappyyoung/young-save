# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-03-16 18:12
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mybackend', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gcloudfiles',
            name='upload_by',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='upload_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='gcloudfiles',
            name='upload_date',
            field=models.CharField(default=b'2017-03-16 11:12:37', max_length=50),
        ),
    ]