# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-11-15 21:54
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0014_auto_20161115_0925'),
    ]

    operations = [
        migrations.CreateModel(
            name='NoteCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(default='NOTE', max_length=20)),
                ('type_name', models.CharField(default='NOTE', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Notes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipient', models.CharField(max_length=50, null=True)),
                ('note', models.TextField(blank=True)),
                ('category', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='note_category', to='tracker.NoteCategory')),
            ],
        ),
        migrations.AlterField(
            model_name='orders',
            name='order_date',
            field=models.CharField(default=b'2016-11-15 13:54:47', max_length=50),
        ),
        migrations.AlterField(
            model_name='orders',
            name='updated',
            field=models.CharField(default=b'2016-11-15 13:54:47', max_length=50),
        ),
        migrations.AlterField(
            model_name='phenotypes',
            name='date',
            field=models.CharField(default=b'2016-11-15 13:54:47', max_length=200),
        ),
        migrations.AlterField(
            model_name='trackinglog',
            name='date',
            field=models.CharField(default=datetime.datetime(2016, 11, 15, 21, 54, 47, 709771, tzinfo=utc), max_length=50),
        ),
        migrations.AddField(
            model_name='notes',
            name='order',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='tracker.Orders'),
        ),
        migrations.AddField(
            model_name='notes',
            name='patient',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tracker.Patients'),
        ),
    ]