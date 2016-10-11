# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-23 19:04
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('mybackend', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderGeneList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genelist', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='genelist', to='mybackend.GeneLists')),
            ],
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patient_id', models.CharField(default=1, max_length=100)),
                ('order_name', models.CharField(max_length=100, unique=True)),
                ('order_date', models.CharField(default=b'2016-09-23 12:04:55', max_length=50)),
                ('updated', models.CharField(default=b'2016-09-23 12:04:55', max_length=50)),
                ('due_date', models.CharField(max_length=50, null=True)),
                ('complete_date', models.CharField(blank=True, default='', max_length=50)),
                ('provider', models.CharField(default='..', max_length=200)),
                ('doctor', models.CharField(default='..', max_length=200)),
                ('facility', models.CharField(default='..', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='OrderStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='CREATED', max_length=20)),
                ('status_name', models.CharField(max_length=50)),
                ('status_desc', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='OrderType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(default='SINGLE', max_length=20)),
                ('type_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='PatientOrderPhenoList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pheno_checklists', models.CharField(blank=True, max_length=400, null=True)),
                ('pheno_valuelists', models.CharField(blank=True, max_length=4000, null=True)),
                ('order', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='pheno_order', to='tracker.Orders')),
            ],
        ),
        migrations.CreateModel(
            name='PatientOrderPhenoType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tracker.Orders')),
            ],
        ),
        migrations.CreateModel(
            name='Patients',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pid', models.CharField(max_length=100, unique=True)),
                ('last_name', models.CharField(blank=True, max_length=50, null=True)),
                ('first_name', models.CharField(blank=True, max_length=50, null=True)),
                ('mrn', models.CharField(max_length=100, unique=True)),
                ('dob', models.CharField(blank=True, max_length=50, null=True)),
                ('race', models.CharField(blank=True, max_length=50, null=True)),
                ('sex', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PhenoTypes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(default=b'2016-09-23 12:04:55', max_length=200)),
                ('name', models.CharField(default='Phenotype', max_length=200)),
                ('type', models.CharField(choices=[('TEXT', 'Text Input'), ('IMAGE', 'Image File'), ('FILE', 'Text / Scan File'), ('ETC', 'ETC'), ('GENELIST', 'Genelists')], default='TEXT', max_length=10)),
                ('desc', models.CharField(default='..', max_length=200)),
                ('image', models.ImageField(blank=True, max_length=400, null=True, upload_to='/Users/s0199669/gcloud/gims/staticfiles/IMAGES/phenotypes/')),
                ('geno_list', models.CharField(blank=True, max_length=400, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Relations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rel', models.CharField(default='SELF', max_length=20)),
                ('rel_name', models.CharField(default='Self', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SampleFiles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_name', models.CharField(default='..', max_length=200)),
                ('file_name', models.CharField(blank=True, max_length=200)),
                ('file_location', models.CharField(default='..', max_length=200)),
                ('file_type', models.CharField(blank=True, max_length=20, null=True)),
                ('loom_id', models.CharField(default='..', max_length=200)),
                ('order', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tracker.Orders')),
            ],
        ),
        migrations.CreateModel(
            name='SampleOrderRel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tracker.Orders')),
                ('relation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tracker.Relations')),
            ],
        ),
        migrations.CreateModel(
            name='Samples',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asn', models.CharField(max_length=50, unique=True)),
                ('number', models.CharField(blank=True, max_length=50, null=True)),
                ('source', models.CharField(default='..', max_length=200)),
                ('type', models.CharField(default='..', max_length=200)),
                ('patient_id', models.CharField(default=1, max_length=100)),
                ('name', models.CharField(default='..', max_length=200)),
                ('desc', models.CharField(default='..', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='TrackingLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(default=datetime.datetime(2016, 9, 23, 19, 4, 55, 29607, tzinfo=utc), max_length=50)),
                ('type', models.CharField(blank=True, max_length=200)),
                ('order', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tracker.Orders')),
                ('owner', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('sample', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tracker.Samples')),
            ],
        ),
        migrations.AddField(
            model_name='sampleorderrel',
            name='sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tracker.Samples'),
        ),
        migrations.AddField(
            model_name='samplefiles',
            name='sample',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tracker.Samples'),
        ),
        migrations.AddField(
            model_name='patientorderphenotype',
            name='patient',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tracker.Patients'),
        ),
        migrations.AddField(
            model_name='patientorderphenotype',
            name='phenotype',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tracker.PhenoTypes'),
        ),
        migrations.AddField(
            model_name='orders',
            name='status',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='OrderStatus', to='tracker.OrderStatus'),
        ),
        migrations.AddField(
            model_name='orders',
            name='type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='OrderType', to='tracker.OrderType'),
        ),
        migrations.AddField(
            model_name='ordergenelist',
            name='order',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='gene_order', to='tracker.Orders'),
        ),
        migrations.AlterUniqueTogether(
            name='ordergenelist',
            unique_together=set([('order', 'genelist')]),
        ),
    ]