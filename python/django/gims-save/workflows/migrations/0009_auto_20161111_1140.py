# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-11-11 19:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflows', '0008_auto_20161111_1004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='labworkflows',
            name='created_date',
            field=models.CharField(default=b'2016-11-11 11:40:29', max_length=50),
        ),
        migrations.AlterField(
            model_name='labworkflows',
            name='update_date',
            field=models.CharField(default=b'2016-11-11 11:40:29', max_length=50),
        ),
    ]
