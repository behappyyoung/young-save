# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-03-22 18:08
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_mysql.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('mybackend', '0004_auto_20170322_1108'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0004_auto_20170322_1108'),
    ]

    operations = [
        migrations.CreateModel(
            name='AffectedStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='UnKnown', max_length=50)),
                ('status_name', models.CharField(default='UnKnown', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Family',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('family_id', models.CharField(default='F_1', max_length=20)),
                ('affectedstatus', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='tracker.AffectedStatus')),
            ],
        ),
        migrations.CreateModel(
            name='FamilyRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(default='Main', max_length=30)),
                ('role_name', models.CharField(default='Main', max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='NoteCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(default='NOTE', max_length=20)),
                ('category_name', models.CharField(default='NOTE', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Notes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_time', models.CharField(default=b'2017-03-22 11:08:55', max_length=200)),
                ('patient_id', models.CharField(default='', max_length=100)),
                ('recipients', models.CharField(blank=True, default='', max_length=400, null=True)),
                ('note', models.TextField(blank=True)),
                ('category', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='NoteCategory', to='tracker.NoteCategory')),
            ],
        ),
        migrations.CreateModel(
            name='OrderGeneList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genelist', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='genelist', to='mybackend.GeneLists')),
            ],
        ),
        migrations.CreateModel(
            name='OrderGroups',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_id', models.CharField(default=1, max_length=50)),
                ('desc', models.CharField(blank=True, default='', max_length=50, null=True)),
                ('run_result', models.CharField(blank=True, default='', max_length=50, null=True)),
                ('affectedstatus', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='tracker.AffectedStatus')),
            ],
        ),
        migrations.CreateModel(
            name='OrderPhenoTypes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Phenotype', max_length=200)),
                ('acc', models.CharField(default='HP:0000000', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='OrderRelations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rel', models.CharField(default='SELF', max_length=20)),
                ('rel_name', models.CharField(default='Self', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='OrderResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.CharField(max_length=20)),
                ('result_desc', models.CharField(max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patient_id', models.CharField(default='', max_length=100)),
                ('epic_order_id', models.CharField(default='', max_length=100)),
                ('order_name', models.CharField(max_length=100)),
                ('order_date', models.CharField(default=b'20170322', max_length=50)),
                ('updated', models.CharField(default=b'2017-03-22 11:08:55', max_length=50)),
                ('due_date', models.CharField(blank=True, max_length=50, null=True)),
                ('complete_date', models.CharField(blank=True, max_length=50, null=True)),
                ('observation_date', models.CharField(max_length=80, null=True)),
                ('provider_name', models.CharField(default='', max_length=200)),
                ('provider_address', models.CharField(default='', max_length=200)),
                ('provider_city', models.CharField(default='', max_length=200)),
                ('provider_state', models.CharField(default='', max_length=200)),
                ('provider_zipcode', models.CharField(default='', max_length=200)),
                ('physician_id', models.CharField(default='', max_length=200)),
                ('physician_firstname', models.CharField(default='', max_length=200)),
                ('physician_lastname', models.CharField(default='', max_length=200)),
                ('physician_phone', models.CharField(max_length=50, null=True)),
                ('patient_account_number', models.CharField(max_length=50, null=True)),
                ('patient_visit_number', models.CharField(max_length=50, null=True)),
                ('facility', models.CharField(max_length=200, null=True)),
                ('physician_phenotype', models.TextField(blank=True, null=True)),
                ('physician_genelist', models.TextField(blank=True, null=True)),
                ('pertinent_negative', models.TextField(blank=True, null=True)),
                ('phenotype', models.CharField(blank=True, max_length=300, null=True)),
                ('genelist', models.CharField(blank=True, max_length=300, null=True)),
                ('desc', models.TextField(blank=True, null=True)),
                ('secondary_findings_flag', models.CharField(max_length=20, null=True)),
                ('secondary_findings_note', models.CharField(blank=True, max_length=200, null=True)),
                ('flag', models.CharField(blank=True, default='', max_length=200, null=True)),
                ('overall_result', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='OrderResult', to='tracker.OrderResult')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='users_UserProfile', to='users.UserProfile')),
            ],
        ),
        migrations.CreateModel(
            name='OrderStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='CREATED', max_length=20)),
                ('status_name', models.CharField(max_length=50)),
                ('status_desc', models.CharField(max_length=200)),
                ('lab_ready', models.BooleanField(default=False)),
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
            name='PatientFiles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_time', models.CharField(default=b'2017-03-22 11:08:55', max_length=200)),
                ('file_title', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('file_name', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('file_path', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('url', models.CharField(blank=True, default='', max_length=200, null=True)),
                ('type', models.CharField(choices=[('IMAGE', 'Image'), ('PDF', 'Text-PDF'), ('WORD', 'Text-Word'), ('TEXT', 'Text')], default='IMAGE', max_length=10)),
                ('file', models.FileField(blank=True, max_length=400, null=True, upload_to='/Users/s0199669/cgsdev/gims/staticfiles/IMAGES/Patient/')),
                ('desc', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('by', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PatientRelations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('main', models.CharField(default='', max_length=100)),
                ('relative', models.CharField(default='', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Patients',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pid', models.CharField(max_length=100, unique=True)),
                ('last_name', models.CharField(max_length=50)),
                ('middle_name', models.CharField(blank=True, max_length=50, null=True)),
                ('first_name', models.CharField(max_length=50)),
                ('mrn', models.CharField(max_length=100)),
                ('dob', models.DateField()),
                ('address', models.CharField(blank=True, default='', max_length=200, null=True)),
                ('phone', models.CharField(blank=True, default='', max_length=20, null=True)),
                ('work_phone', models.CharField(blank=True, default='', max_length=200, null=True)),
                ('ethnicity', models.CharField(blank=True, default='', max_length=50, null=True)),
                ('sex', models.CharField(max_length=10)),
                ('memo', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Pedigree',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pedigree_json', models.CharField(default='[]', max_length=2000)),
                ('pedigree_image', models.ImageField(blank=True, max_length=400, null=True, upload_to='/Users/s0199669/cgsdev/gims/staticfiles/IMAGES/Pedigree/')),
                ('patient', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tracker.Patients')),
            ],
        ),
        migrations.CreateModel(
            name='PeopleRelations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rel', models.CharField(default='', max_length=20)),
                ('rel_name', models.CharField(default='', max_length=100)),
                ('allowed_sex', models.CharField(default='', max_length=20)),
                ('back_relation_female', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='female', to='tracker.PeopleRelations')),
                ('back_relation_male', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='male', to='tracker.PeopleRelations')),
            ],
        ),
        migrations.CreateModel(
            name='QCResults',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('run_id', models.CharField(max_length=100)),
                ('pass_fail', models.BooleanField(default=False)),
                ('result_json', django_mysql.models.JSONField(default=dict)),
                ('process_date', models.DateTimeField(default=datetime.datetime.now)),
            ],
        ),
        migrations.CreateModel(
            name='SampleContainer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cid', models.CharField(max_length=20)),
                ('desc', models.CharField(blank=True, default=' ', max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SampleFiles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_name', models.CharField(max_length=200, null=True)),
                ('file_name', models.CharField(blank=True, max_length=200, null=True)),
                ('file_location', models.CharField(max_length=200)),
                ('file_type', models.CharField(blank=True, max_length=20, null=True)),
                ('loom_id', models.CharField(max_length=200, null=True)),
                ('order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tracker.Orders')),
            ],
        ),
        migrations.CreateModel(
            name='SampleOrderRel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('container', models.CharField(max_length=20, null=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tracker.Orders')),
                ('patient', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tracker.Patients')),
            ],
        ),
        migrations.CreateModel(
            name='Samples',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asn', models.CharField(max_length=50, unique=True)),
                ('source', models.CharField(default='..', max_length=200)),
                ('type', models.CharField(default='..', max_length=200)),
                ('collection_date', models.DateTimeField(blank=True, null=True)),
                ('patient_id', models.CharField(default=1, max_length=100)),
                ('name', models.CharField(max_length=200, null=True)),
                ('volume', models.FloatField(blank=True, default=100)),
                ('desc', models.TextField(blank=True, null=True)),
                ('note', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SampleStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='COLLECTED', max_length=20)),
                ('status_name', models.CharField(max_length=50)),
                ('status_desc', models.CharField(max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SORelations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rel', models.CharField(default='SELF', max_length=20)),
                ('rel_name', models.CharField(default='Self', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Threshold',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, null=True)),
                ('current_threshold', models.IntegerField(default=1)),
                ('create_date', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('threshold_json', django_mysql.models.JSONField(default=dict)),
            ],
        ),
        migrations.AddField(
            model_name='samples',
            name='status',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='SampleStatus', to='tracker.SampleStatus'),
        ),
        migrations.AddField(
            model_name='sampleorderrel',
            name='relation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tracker.SORelations'),
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
            model_name='samplecontainer',
            name='sample',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tracker.Samples'),
        ),
        migrations.AddField(
            model_name='qcresults',
            name='sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tracker.Samples'),
        ),
        migrations.AddField(
            model_name='qcresults',
            name='threshold',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tracker.Threshold'),
        ),
        migrations.AddField(
            model_name='patientrelations',
            name='relationship',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tracker.PeopleRelations'),
        ),
        migrations.AddField(
            model_name='patientfiles',
            name='patient',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tracker.Patients'),
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
            model_name='orderphenotypes',
            name='order',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='tracker.Orders'),
        ),
        migrations.AddField(
            model_name='ordergroups',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grouped_order', to='tracker.Orders'),
        ),
        migrations.AddField(
            model_name='ordergroups',
            name='relation',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tracker.OrderRelations'),
        ),
        migrations.AddField(
            model_name='ordergenelist',
            name='order',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='gene_order', to='tracker.Orders'),
        ),
        migrations.AddField(
            model_name='notes',
            name='order',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='tracker.Orders'),
        ),
        migrations.AddField(
            model_name='notes',
            name='recipient',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recipient', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='notes',
            name='writer',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='writer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='family',
            name='patient',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tracker.Patients'),
        ),
        migrations.AddField(
            model_name='family',
            name='role',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tracker.FamilyRole'),
        ),
        migrations.AlterUniqueTogether(
            name='ordergenelist',
            unique_together=set([('order', 'genelist')]),
        ),
    ]
