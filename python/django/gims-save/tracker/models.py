from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.models import User
from gims import settings
from users.models import UserProfile
from mybackend.models import PhenoTypeLists, GeneLists

FILE_TYPES = (
    ('IMAGE', 'Image'),
    ('PDF', 'Text-PDF'),
    ('WORD', 'Text-Word'),
    ('TEXT', 'Text'),
)


class Patients(models.Model):
    pid = models.CharField(max_length=100, unique=True, null=False)            # pid = mrn for now
    last_name = models.CharField(max_length=50,  null=False)
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    first_name = models.CharField(max_length=50,  null=False)
    mrn = models.CharField(max_length=100, null=False, blank=False)           # patient ID for now
    dob = models.DateField(null=False)
    address = models.CharField(max_length=200,  null=True, blank=True, default='')
    phone = models.CharField(max_length=20,  null=True, blank=True, default='')
    work_phone = models.CharField(max_length=200,  null=True, blank=True, default='')
    ethnicity = models.CharField(max_length=50,  null=True, blank=True, default='')
    sex = models.CharField(max_length=10, null=False)
    memo = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.pid


class PatientFiles(models.Model):
    update_time = models.CharField(max_length=200, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    patient = models.ForeignKey('Patients', null=False, default=1)
    file_title = models.CharField(max_length=100, null=True, blank=True, default='')
    file_name = models.CharField(max_length=100, null=True, blank=True, default='')
    file_path = models.CharField(max_length=100, null=True, blank=True, default='')
    url = models.CharField(max_length=200, null=True, blank=True, default='')
    type = models.CharField(max_length=10, choices=FILE_TYPES, default='IMAGE')
    file = models.FileField(max_length=400, upload_to=settings.MEDIA_ROOT+'/Patient/',  null=True, blank=True)  # for form
    desc = models.CharField(max_length=100, null=True, blank=True, default='')


class AffectedStatus(models.Model):
    status = models.CharField(max_length=50, default='UnKnown', null=False)
    status_name = models.CharField(max_length=50, default='UnKnown', null=False)

    def __unicode__(self):
        return self.status_name


class Family(models.Model):         # patient's groups
    family_id = models.CharField(max_length=20, null=False, default='F_1')
    patient = models.ForeignKey('Patients', null=False, default=1)
    role = models.ForeignKey('FamilyRole', on_delete=models.CASCADE, null=False, default=1)
    affectedstatus = models.ForeignKey('AffectedStatus', on_delete=models.CASCADE, null=True, default=1)


class FamilyRole(models.Model):
    role = models.CharField(max_length=30, null=False, default='Main')
    role_name = models.CharField(max_length=30, null=False, default='Main')

    def __unicode__(self):
        return self.role_name


class PeopleRelations(models.Model):
    rel = models.CharField(max_length=20, default='')
    rel_name = models.CharField(max_length=100, null=False, default='')
    allowed_sex = models.CharField(max_length=20, null=False, default='')
    back_relation_male = models.ForeignKey('self',related_name="male", null=True, blank=True)
    back_relation_female = models.ForeignKey('self', related_name="female", null=True, blank=True)

    def __unicode__(self):
        return self.rel_name


class PatientRelations(models.Model):
    main = models.CharField(max_length=100, default='')             # patient id = MRN
    relationship = models.ForeignKey('PeopleRelations', on_delete=models.CASCADE, null=False)
    relative = models.CharField(max_length=100, default='')         # patient id = MRN


class Samples(models.Model):
    asn = models.CharField(max_length=50, unique=True, null=False)              # sample's unique code
    source = models.CharField(max_length=200, default='..')
    type = models.CharField(max_length=200, default='..')
    collection_date = models.DateTimeField(auto_now=False, null=True, blank=True)
    patient_id = models.CharField(max_length=100, default=1, null=False)
    status = models.ForeignKey('SampleStatus', related_name="SampleStatus", on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=200, null=True)
    desc = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.name


class SampleContainer(models.Model):
    sample = models.ForeignKey('Samples', on_delete=models.CASCADE, null=False, default=1)
    cid = models.CharField(max_length=20, null=False)
    desc = models.CharField(max_length=200, null=True, blank=True, default=' ')


class SampleFiles(models.Model):
    sample = models.ForeignKey('Samples', on_delete=models.CASCADE, null=False, default=1)
    order = models.ForeignKey('Orders', on_delete=models.CASCADE, null=True)
    channel_name = models.CharField(max_length=200, null=True)
    file_name = models.CharField(max_length=200, blank=True, null=True)
    file_location = models.CharField(max_length=200, null=False)
    file_type = models.CharField(max_length=20, null=True, blank=True)
    loom_id = models.CharField(max_length=200, null=True)

    def __unicode__(self):
        return self.loom_id


class SampleStatus(models.Model):
    status = models.CharField(max_length=20, default='COLLECTED')
    status_name = models.CharField(max_length=50, null=False)
    status_desc = models.CharField(max_length=200, null=True)

    def __unicode__(self):
        return self.status_name


class OrderStatus(models.Model):
    status = models.CharField(max_length=20, default='CREATED')
    status_name = models.CharField(max_length=50, null=False)
    status_desc = models.CharField(max_length=200, null=False)
    lab_ready = models.BooleanField(default=False)

    def __unicode__(self):
        return self.status_name

LabOrder_Status = (
    ('COLLECTED', 'Sample Collected'),
    ('READY', 'Ready For Lab'),
    ('QSTART', 'Start Quantification'),
    ('QFAIL', 'Quantification Failed'),
    ('QREDO', 'Quantification Failed - Need Adjustment'),
    ('QPASS', 'Quantification Passed'),
    ('FSTART', 'Start Fluidigm'),
    ('FDONE', 'Fluidigm Complete'),
)


class LabOrderStatus(models.Model):
    labstatus = models.CharField(max_length=20, default='COLLECTED')
    labstatus_name = models.CharField(max_length=50, null=False)
    status_desc = models.CharField(max_length=200, null=True)

    def __unicode__(self):
        return self.labstatus_name


class OrderType(models.Model):
    type = models.CharField(max_length=20, default='SINGLE')
    type_name = models.CharField(max_length=50, null=False)

    def __unicode__(self):
        return self.type_name


class Orders(models.Model):
    patient_id = models.CharField(max_length=100, default='')
    epic_order_id = models.CharField(max_length=100, default='')
    order_name = models.CharField(max_length=100, null=False)
    order_date = models.CharField(max_length=50, null=False, default=datetime.now().strftime('%Y%m%d'))
    updated = models.CharField(max_length=50, null=False, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    due_date = models.CharField(max_length=50, null=True, blank=True)
    complete_date = models.CharField(max_length=50, blank=True, null=True)
    observation_date = models.CharField(max_length=80, null=True)
    status = models.ForeignKey('OrderStatus', related_name="OrderStatus", on_delete=models.CASCADE, default=1)
    # lab_status = models.CharField(choices=LabOrder_Status, max_length=20, default=' ')
    lab_status = models.ForeignKey('LabOrderStatus', related_name="LabOrderStatus", on_delete=models.CASCADE, default=1)
    type = models.ForeignKey('OrderType',related_name='OrderType', on_delete=models.CASCADE, default=1)
    provider_name = models.CharField(max_length=200, default='')
    provider_address = models.CharField(max_length=200, default='')
    provider_city = models.CharField(max_length=200, default='')
    provider_state = models.CharField(max_length=200, default='')
    provider_zipcode = models.CharField(max_length=200, default='')
    physician_id = models.CharField(max_length=200, default='')
    physician_firstname = models.CharField(max_length=200, default='')
    physician_lastname = models.CharField(max_length=200, default='')
    physician_phone = models.CharField(max_length=50, null=True)
    patient_account_number = models.CharField(max_length=50, null=True)
    patient_visit_number = models.CharField(max_length=50, null=True)
    facility = models.CharField(max_length=200, null=True)
    owner = models.ForeignKey('users.UserProfile', related_name='users_UserProfile', on_delete=models.CASCADE, null=True)
    physician_phenotype = models.TextField(null=True, blank=True)  # physician phenotype string
    physician_genelist = models.TextField(null=True, blank=True)
    pertinent_negative = models.TextField(null=True, blank=True)
    phenotype = models.CharField(max_length=300, null=True, blank=True)
    desc = models.TextField(blank=True, null=True)
    # report_secondary_findings = models.CharField(max_length=200, null=True, blank=True, default='')
    flag = models.CharField(max_length=200, null=True, blank=True, default='')

    def __unicode__(self):
        return self.order_name

    def save(self, **kwargs):
        if not self.id:
            self.order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        super(Orders, self).save()


class OrderRelations(models.Model):
    rel = models.CharField(max_length=20, default='SELF')
    rel_name = models.CharField(max_length=100, null=False, default='Self')

    def __unicode__(self):
        return self.rel_name

'''
    Order Groups
'''


class OrderGroups(models.Model):
    group_id = models.CharField(max_length=50, default=1)
    order = models.ForeignKey('Orders', related_name='grouped_order', on_delete=models.CASCADE, null=False)
    relation = models.ForeignKey('OrderRelations', on_delete=models.CASCADE, default=1)
    affectedstatus = models.ForeignKey('AffectedStatus', on_delete=models.CASCADE, null=True, default=1)
    desc = models.CharField(max_length=50, blank=True, null=True, default='')
    run_result = models.CharField(max_length=50, blank=True, null=True, default='')


class OrderGeneList(models.Model):
    order = models.ForeignKey(Orders, related_name="gene_order", on_delete=models.CASCADE, default=1)
    genelist = models.ForeignKey(GeneLists, related_name='genelist', on_delete=models.CASCADE, default=1)

    class Meta:
        unique_together = ["order", "genelist"]


class OrderPhenoTypes(models.Model):
    order = models.ForeignKey('Orders', related_name="orders",  on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=200, default='Phenotype')
    acc = models.CharField(max_length=50, default='HP:0000000')  # hpo id


class NoteCategory(models.Model):
    category = models.CharField(max_length=20, default='NOTE')
    category_name = models.CharField(max_length=50, null=False, default='NOTE')

    def __unicode__(self):
        return self.category_name


class Notes(models.Model):
    writer = models.ForeignKey(User, related_name='writer', blank=True, null=True, default='')
    update_time = models.CharField(max_length=200, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    category = models.ForeignKey('NoteCategory', related_name='NoteCategory', on_delete=models.CASCADE, default=1)
    order = models.ForeignKey('Orders', on_delete=models.CASCADE, blank=True, null=True, default='')
    patient_id = models.CharField(max_length=100, default='')
    recipient = models.ForeignKey(User, related_name='recipient', blank=True, null=True, default='')
    recipients = models.CharField(max_length=400, blank=True, null=True, default='')
    note = models.TextField(blank=True)


class SORelations(models.Model):
    rel = models.CharField(max_length=20, default='SELF')
    rel_name = models.CharField(max_length=100, null=False, default='Self')

    def __unicode__(self):
        return self.rel_name


class SampleOrderRel(models.Model):
    sample = models.ForeignKey('Samples', on_delete=models.CASCADE, null=False)
    order = models.ForeignKey('Orders', on_delete=models.CASCADE, null=False)
    relation = models.ForeignKey('SORelations', on_delete=models.CASCADE, null=False)
    patient = models.ForeignKey('Patients', on_delete=models.CASCADE, null=False, default=1)
    container = models.CharField(max_length=20, null=True)             # adding to sample when lab choose container for the sample


############################################################################################################# old version


class PatientOrderPhenoList(models.Model):
    order = models.ForeignKey(Orders, related_name="pheno_order", on_delete=models.CASCADE, default=1)
    pheno_checklists = models.CharField(max_length=400, null=True, blank=True)   # list of phenotypes belong to order / patient " id,id,id,, "
    pheno_valuelists = models.CharField(max_length=4000, null=True, blank=True)  # list of phenotypes belong to order / patient { id, value }


class PatientOrderPhenoType(models.Model):
    order = models.ForeignKey('Orders', on_delete=models.CASCADE, default=1)
    patient = models.ForeignKey('Patients', on_delete=models.CASCADE, default=1)
    phenotype = models.ForeignKey('PhenoTypes', on_delete=models.CASCADE, default=1)


PHENOTYPE_TYPE = (
    ('TEXT', 'Text Input'), ('IMAGE', 'Image File'), ('FILE' , 'Text / Scan File'), ( 'ETC', 'ETC'), ( 'GENELIST', 'Genelists')
)


class PhenoTypes(models.Model):
    date = models.CharField(max_length=200, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    name = models.CharField(max_length=200, default='Phenotype')
    type = models.CharField(max_length=10, choices=PHENOTYPE_TYPE, default='TEXT')
    desc = models.CharField(max_length=200, default='..')
    image = models.ImageField(max_length=400, upload_to=settings.MEDIA_ROOT+'/Phenotypes/',  null=True, blank=True)
    geno_list = models.CharField(max_length=400, blank=True, null=True)

    def __unicode__(self):
        return self.name


class Pedigree(models.Model):
    patient = models.ForeignKey('Patients', null=False, default=1)
    pedigree_json = models.CharField(max_length=2000, default='[]')
    pedigree_image = models.ImageField(max_length=400, upload_to=settings.MEDIA_ROOT+'/Pedigree/',  null=True, blank=True)


#################
class TrackingLog(models.Model):
    date = models.CharField(max_length=50, null=False,default=timezone.now())
    owner = models.ForeignKey(User, default=1)
    type = models.CharField(max_length=200, blank=True)
    sample = models.ForeignKey('Samples', on_delete=models.CASCADE, default=1)
    order = models.ForeignKey('Orders', on_delete=models.CASCADE, default=1)

    # def log(self):
    #     self.date = timezone.now()
    #     self.save()