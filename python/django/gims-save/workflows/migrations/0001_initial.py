# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-03-22 18:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tracker', '0002_auto_20170322_1109'),
    ]

    operations = [
        migrations.CreateModel(
            name='LabStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('labstatus', models.CharField(default='QSTART', max_length=20)),
                ('labstatus_name', models.CharField(max_length=50)),
                ('status_desc', models.CharField(max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LabType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('labtype', models.CharField(default='Q', max_length=20)),
                ('labtype_name', models.CharField(max_length=50)),
                ('type_desc', models.CharField(max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LabWorkFlows',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('created_date', models.CharField(default=b'2017-03-22 11:09:07', max_length=50)),
                ('updated_date', models.CharField(default=b'2017-03-22 11:09:07', max_length=50)),
                ('samples_list', models.CharField(blank=True, max_length=200, null=True)),
                ('username', models.CharField(max_length=50, null=True)),
                ('result_data', models.CharField(max_length=1000, null=True)),
                ('status', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='workflows.LabStatus')),
                ('type', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='workflows.LabType')),
            ],
        ),
        migrations.CreateModel(
            name='LabWorkFlowStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tube_number', models.IntegerField()),
                ('container', models.CharField(blank=True, default=1, max_length=10, null=True)),
                ('result', models.CharField(max_length=200, null=True)),
                ('order', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tracker.Orders')),
                ('sample', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tracker.Samples')),
                ('status', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='workflows.LabStatus')),
                ('workflow', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='workflows.LabWorkFlows')),
            ],
        ),
        migrations.CreateModel(
            name='LabWorkFlowType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=20)),
                ('type_name', models.CharField(max_length=50)),
                ('desc', models.CharField(max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Workflows',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('version', models.CharField(default='1', max_length=20)),
                ('workflow_id', models.CharField(max_length=200)),
                ('inputs', models.CharField(blank=True, max_length=400, null=True)),
                ('fixed_inputs', models.CharField(blank=True, max_length=400, null=True)),
                ('desc', models.CharField(blank=True, max_length=200, null=True)),
                ('status', models.CharField(choices=[('A', 'Active'), ('I', 'In Active')], default='A', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='WorkflowType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=20)),
                ('type_name', models.CharField(max_length=50)),
                ('desc', models.CharField(max_length=200, null=True)),
                ('status', models.CharField(choices=[('A', 'Active'), ('I', 'In Active')], default='A', max_length=10)),
            ],
            managers=[
                ('wf_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='workflows',
            name='type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='workflows.WorkflowType'),
        ),
    ]
