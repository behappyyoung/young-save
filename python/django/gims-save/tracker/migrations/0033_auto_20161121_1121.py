# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-11-21 19:21
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0032_auto_20161118_1321'),
    ]

    operations = [
        migrations.CreateModel(
            name='SampleContainer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cid', models.CharField(blank=True, default=' ', max_length=20, null=True)),
                ('desc', models.CharField(blank=True, default=' ', max_length=200, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='peoplerelations',
            name='allowed_sex',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='notes',
            name='update_time',
            field=models.CharField(default=b'2016-11-21 11:21:26', max_length=200),
        ),
        migrations.AlterField(
            model_name='orders',
            name='order_date',
            field=models.CharField(default=b'2016-11-21 11:21:26', max_length=50),
        ),
        migrations.AlterField(
            model_name='orders',
            name='updated',
            field=models.CharField(default=b'2016-11-21 11:21:26', max_length=50),
        ),
        migrations.AlterField(
            model_name='phenotypes',
            name='date',
            field=models.CharField(default=b'2016-11-21 11:21:26', max_length=200),
        ),
        migrations.AlterField(
            model_name='samples',
            name='container',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='trackinglog',
            name='date',
            field=models.CharField(default=datetime.datetime(2016, 11, 21, 19, 21, 26, 317065, tzinfo=utc), max_length=50),
        ),
        migrations.AddField(
            model_name='samplecontainer',
            name='sample',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tracker.Samples'),
        ),
    ]