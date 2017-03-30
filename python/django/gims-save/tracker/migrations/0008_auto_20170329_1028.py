# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-03-29 17:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0007_auto_20170328_0822'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='patients',
            name='address',
        ),
        migrations.AddField(
            model_name='patients',
            name='address1',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='patients',
            name='address2',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='patients',
            name='city',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='patients',
            name='state',
            field=models.CharField(max_length=45, null=True),
        ),
        migrations.AddField(
            model_name='patients',
            name='zip',
            field=models.CharField(max_length=45, null=True),
        ),
        migrations.AlterField(
            model_name='notes',
            name='update_time',
            field=models.CharField(default=b'2017-03-29 10:28:43', max_length=200),
        ),
        migrations.AlterField(
            model_name='orders',
            name='order_date',
            field=models.CharField(default=b'20170329', max_length=50),
        ),
        migrations.AlterField(
            model_name='orders',
            name='updated',
            field=models.CharField(default=b'2017-03-29 10:28:43', max_length=50),
        ),
        migrations.AlterField(
            model_name='patientfiles',
            name='update_time',
            field=models.CharField(default=b'2017-03-29 10:28:43', max_length=200),
        ),
        migrations.AlterField(
            model_name='patients',
            name='ethnicity',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='patients',
            name='phone',
            field=models.CharField(max_length=45, null=True),
        ),
        migrations.AlterField(
            model_name='patients',
            name='work_phone',
            field=models.CharField(max_length=45, null=True),
        ),
    ]
