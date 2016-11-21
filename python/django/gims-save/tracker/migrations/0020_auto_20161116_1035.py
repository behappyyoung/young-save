# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-11-16 18:35
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0019_auto_20161116_1027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='order_date',
            field=models.CharField(default=b'2016-11-16 10:35:41', max_length=50),
        ),
        migrations.AlterField(
            model_name='orders',
            name='owner',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='orders',
            name='updated',
            field=models.CharField(default=b'2016-11-16 10:35:41', max_length=50),
        ),
        migrations.AlterField(
            model_name='phenotypes',
            name='date',
            field=models.CharField(default=b'2016-11-16 10:35:41', max_length=200),
        ),
        migrations.AlterField(
            model_name='trackinglog',
            name='date',
            field=models.CharField(default=datetime.datetime(2016, 11, 16, 18, 35, 41, 152848, tzinfo=utc), max_length=50),
        ),
    ]
