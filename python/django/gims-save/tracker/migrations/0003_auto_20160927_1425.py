# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-27 21:25
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0002_auto_20160926_1048'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderPhenoTypes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Phenotype', max_length=200)),
                ('acc', models.CharField(default='HP:0000001', max_length=50)),
            ],
        ),
        migrations.AlterField(
            model_name='orders',
            name='order_date',
            field=models.CharField(default=b'2016-09-27 14:25:18', max_length=50),
        ),
        migrations.AlterField(
            model_name='orders',
            name='updated',
            field=models.CharField(default=b'2016-09-27 14:25:18', max_length=50),
        ),
        migrations.AlterField(
            model_name='phenotypes',
            name='date',
            field=models.CharField(default=b'2016-09-27 14:25:18', max_length=200),
        ),
        migrations.AlterField(
            model_name='trackinglog',
            name='date',
            field=models.CharField(default=datetime.datetime(2016, 9, 27, 21, 25, 18, 645301, tzinfo=utc), max_length=50),
        ),
        migrations.AddField(
            model_name='orderphenotypes',
            name='order',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tracker.Orders'),
        ),
    ]
