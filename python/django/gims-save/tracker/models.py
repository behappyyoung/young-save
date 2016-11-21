from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.models import User
from gims import settings
from mybackend.models import PhenoTypeLists, GeneLists


class Relations(models.Model):
    rel = models.CharField(max_length=20, default='SELF')
    rel_name = models.CharField(max_length=100, null=False, default='Self')

    def __unicode__(self):
        return self.rel_name


class Patients(models.Model):
    pid = models.CharField(max_length=100, unique=True, null=False)            # pid = mrn for now
    last_name = models.CharField(max_length=50,  null=True, blank=True)
    middle_name = models.CharField(max_length=50, default=' ')
    first_name = models.CharField(max_length=50,  null=True, blank=True)
    mrn = models.CharField(max_length=100, unique=True, null=False)           # patient ID for now
    dob = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=200,  null=True, blank=True)
    phone = models.CharField(max_length=20,  null=True, blank=True)
    work_phone = models.CharField(max_length=200,  null=True, blank=True)
    ethnicity = models.CharField(max_length=50,  null=True, blank=True)
    sex = models.CharField(max_length=10,  null=True, blank=True)

    def __unicode__(self):
        return self.mrn


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
    container = models.CharField(max_length=200, blank=True, null=True)            # list of container JIC
    source = models.CharField(max_length=200, default='..')
    type = models.CharField(max_length=200, default='..')
    collection_date = models.DateTimeField(auto_now=False, null=True, blank=True)
    patient_id = models.CharField(max_length=100, default=1)
    name = models.CharField(max_length=200, default='..')
    desc = models.TextField(blank=True)

    def __unicode__(self):
        return self.name


class SampleContainer(models.Model):
    sample = models.ForeignKey('Samples', on_delete=models.CASCADE, null=False, default=1)
    cid = models.CharField(max_length=20, null=True, blank=True, default=' ')
    desc = models.CharField(max_length=200, null=True, blank=True, default=' ')


class SampleFiles(models.Model):
    sample = models.ForeignKey('Samples', on_delete=models.CASCADE, null=False, default=1)
    order = models.ForeignKey('Orders', on_delete=models.CASCADE, null=False, default=1)
    channel_name = models.CharField(max_length=200, default='..')
    file_name = models.CharField(max_length=200, blank=True)
    file_location = models.CharField(max_length=200, default='..')
    file_type = models.CharField(max_length=20, null=True, blank=True)
    loom_id = models.CharField(max_length=200, default='..')

    def __unicode__(self):
        return self.loom_id


class OrderStatus(models.Model):
    status = models.CharField(max_length=20, default='CREATED')
    status_name = models.CharField(max_length=50, null=False)
    status_desc = models.CharField(max_length=200, null=False)

    def __unicode__(self):
        return self.status_name


class OrderType(models.Model):
    type = models.CharField(max_length=20, default='SINGLE')
    type_name = models.CharField(max_length=50, null=False)

    def __unicode__(self):
        return self.type_name


class Orders(models.Model):
    patient_id = models.CharField(max_length=100, default=1)
    order_name = models.CharField(max_length=100, null=False, unique=True)
    order_date = models.CharField(max_length=50, null=False, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    updated = models.CharField(max_length=50, null=False, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    due_date = models.CharField(max_length=50, null=True)
    complete_date = models.CharField(max_length=50, blank=True, default='')
    status = models.ForeignKey('OrderStatus', related_name="OrderStatus", on_delete=models.CASCADE, default=1)
    type = models.ForeignKey('OrderType',related_name='OrderType', on_delete=models.CASCADE, default=1)
    provider = models.CharField(max_length=200, default='..')
    doctor = models.CharField(max_length=200, default='..')
    doctor_phone = models.CharField(max_length=50, null=True, blank=True)
    facility = models.CharField(max_length=200, default='..')
    owner = models.CharField(max_length=50, null=True)      # user id
    phenotype = models.CharField(max_length=300, null=True, blank=True) # physician phenotype string
    desc = models.TextField(blank=True)

    def __unicode__(self):
        return self.order_name

    def save(self, **kwargs):
        if not self.id:
            self.order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        super(Orders, self).save()


class SampleOrderRel(models.Model):
    sample = models.ForeignKey('Samples', on_delete=models.CASCADE, null=False)
    order = models.ForeignKey('Orders', on_delete=models.CASCADE, null=False)
    relation = models.ForeignKey('Relations', on_delete=models.CASCADE, null=False)
    affected_Status = models.CharField(max_length=50, default='unknown')


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
    update_time = models.CharField(max_length=200, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    category = models.ForeignKey('NoteCategory', related_name='NoteCategory', on_delete=models.CASCADE, default=1)
    order = models.ForeignKey('Orders', on_delete=models.CASCADE, blank=True, null=True, default='')
    patient_id = models.CharField(max_length=100, default='')
    recipient = models.ForeignKey(User, blank=True, null=True, default='')
    note = models.TextField(blank=True)


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
    patient_id = models.CharField(max_length=50, default='')
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