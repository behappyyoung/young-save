# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-03-22 18:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mybackend', '0003_auto_20170321_0858'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gcloudfiles',
            name='upload_date',
            field=models.CharField(default=b'2017-03-22 11:08:55', max_length=50),
        ),
    ]
