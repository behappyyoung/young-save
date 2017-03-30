from __future__ import unicode_literals

from django.db import models
from datetime import datetime
from tracker.models import Orders, Samples, OrderType
# Create your models here.

STATUS_CODE = (
    ('A', 'Active'),
    ('I', 'In Active')
)


class WorkflowManager(models.Manager):          # override manager to show only active workflows
    def get_queryset(self):
        return super(WorkflowManager, self).get_queryset().filter(status='A')


class WorkflowType(models.Model):
    type = models.CharField(max_length=20, null=False)
    type_name = models.CharField(max_length=50, null=False)
    desc = models.CharField(max_length=200, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CODE, default='A')
    wf_objects = WorkflowManager()
    objects = models.Manager()

    def __unicode__(self):
        return self.type_name


class Workflows(models.Model):
    order_type = models.ForeignKey('tracker.OrderType', default=1)
    type = models.CharField(max_length=40, null=True)
    order_type = models.ForeignKey('tracker.OrderType', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, null=False)
    version = models.CharField(max_length=20, default='1.0')
    workflow_id = models.CharField(max_length=200, null=False)
    inputs = models.CharField(max_length=400, null=True, blank=True)
    fixed_inputs = models.CharField(max_length=400, null=True, blank=True)
    desc = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CODE, default='A')
    objects = models.Manager()
    wf_objects = WorkflowManager()

    def __unicode__(self):
        return self.workflow_id


class LabWorkFlowType(models.Model):
    type = models.CharField(max_length=20, null=False)
    type_name = models.CharField(max_length=50, null=False)
    desc = models.CharField(max_length=200, null=True)


LabWorkFlow_Type = (
    ('Q', 'Quantification'),
    ('F', 'Fluidigm'),
    ('S', 'Sanger Confirmation')
)

LabWorkFlow_Status = (
    ('QSTART', 'Start Quantification'),
    ('QFAIL', 'Quantification Failed'),
    ('QREDO', 'Quantification Failed - Need Adjustment'),
    ('QPASS', 'Quantification Passed'),
    ('FSTART', 'Start Fluidigm'),
    ('FDONE', 'Fluidigm Complete'),
)


class LabType(models.Model):
    labtype = models.CharField(max_length=20, default='Q')
    labtype_name = models.CharField(max_length=50, null=False)
    type_desc = models.CharField(max_length=200, null=True)

    def __unicode__(self):
        return self.labtype_name


class LabStatus(models.Model):
    labstatus = models.CharField(max_length=20, default='QSTART')
    labstatus_name = models.CharField(max_length=50, null=False)
    status_desc = models.CharField(max_length=200, null=True)

    def __unicode__(self):
        return self.labstatus_name


class LabWorkFlowStatus(models.Model):
    workflow = models.ForeignKey('LabWorkFlows',  default=1)
    tube_number = models.IntegerField(blank=False)
    order = models.ForeignKey('tracker.Orders', default=1)
    sample = models.ForeignKey('tracker.Samples', default=1)
    container = models.CharField(max_length=10, default=1, null=True, blank=True)
    status = models.ForeignKey('LabStatus', default=1)
    result = models.CharField(max_length=200, null=True)


class LabWorkFlows(models.Model):
    name = models.CharField(max_length=100, null=False)
    created_date = models.CharField(max_length=50, null=False, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    updated_date = models.CharField(max_length=50, null=False, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    samples_list = models.CharField(max_length=200, null=True, blank=True)
    type = models.ForeignKey('LabType', default=1)
    status = models.ForeignKey('LabStatus', default=1)
    username = models.CharField(max_length=50, null=True)
    result_data = models.CharField(max_length=1000, null=True)
    objects = models.Manager()
    wf_objects = WorkflowManager()

    def __unicode__(self):
        return self.name

