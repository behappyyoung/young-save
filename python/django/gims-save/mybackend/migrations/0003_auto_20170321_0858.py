# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-03-21 15:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mybackend', '0002_auto_20170316_1112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gcloudfiles',
            name='upload_date',
            field=models.CharField(default=b'2017-03-21 08:58:17', max_length=50),
        ),
    ]
