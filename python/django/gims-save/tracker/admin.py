from django.contrib import admin
from django import forms

# Register your models here.
from .models import Samples, Orders, OrderStatus, OrderType, OrderGroups, OrderRelations, SampleFiles\
    , Patients, PeopleRelations, NoteCategory, Notes, \
    PatientFiles, SORelations, SampleOrderRel, FamilyRole, AffectedStatus


class TrackingAdmin(admin.ModelAdmin):
    list_display = ['date', 'owner', 'sample']

    def get_sample(self, obj):
        return obj.sample.number


class SampleAdmin(admin.ModelAdmin):
    list_display = ['asn','name', 'source', 'type', 'collection_date', 'desc', 'note']


class SampleFileAdmin(admin.ModelAdmin):
    list_display = ['sample', 'channel_name', 'file_location', 'loom_id', 'file_type']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_name', 'patient_id','epic_order_id', 'order_date', 'due_date', 'status', 'physician_phone']


class StatusAdmin(admin.ModelAdmin):
    list_display = ['status', 'status_name', 'status_desc']


class LabStatusAdmin(admin.ModelAdmin):
    list_display = ['labstatus', 'labstatus_name', 'status_desc']


class OrderTypeAdmin(admin.ModelAdmin):
    list_display = ['type', 'type_name']


class OrderRelationsAdmin(admin.ModelAdmin):
    list_display = ['rel', 'rel_name']


class OrderGroupsAdmin(admin.ModelAdmin):
    list_display = ['group_id', 'order', 'relation', 'affectedstatus', 'desc']


class SORelationsAdmin(admin.ModelAdmin):
    list_display = ['rel', 'rel_name']


class SampleOrderRelAdmin(admin.ModelAdmin):
    list_display = ['order', 'sample', 'relation']


class PatientsAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'mrn', 'dob', 'ethnicity', 'sex']


class PeopleRelationsAdmin(admin.ModelAdmin):
    list_display = ['rel', 'rel_name', 'back_relation_male', 'back_relation_female']


class PatientFilesAdmin(admin.ModelAdmin):
    list_display = ['update_time', 'patient', 'file_title', 'file_name', 'file_path', 'type', 'desc', 'url']


class FamilyRoleAdmin(admin.ModelAdmin):
    list_display = ['role', 'role_name']


class AffectedStatusAdmin(admin.ModelAdmin):
    list_display = ['status', 'status_name']


class PatientOrderPhenoListAdmin(admin.ModelAdmin):
    list_display =  [ 'order', 'pheno_checklists', 'pheno_valuelists']


class NoteCategoryAdmin(admin.ModelAdmin):
    list_display = ['category', 'category_name']


class NotesAdmin(admin.ModelAdmin):
    list_display = ['category','order', 'patient_id', 'recipient', 'note']


admin.site.register(Samples, SampleAdmin)
admin.site.register(SampleFiles, SampleFileAdmin)
admin.site.register(Orders, OrderAdmin)
admin.site.register(OrderStatus, StatusAdmin)
admin.site.register(OrderType, OrderTypeAdmin)
admin.site.register(OrderRelations, OrderRelationsAdmin)
admin.site.register(OrderGroups, OrderGroupsAdmin)
admin.site.register(Patients, PatientsAdmin)
admin.site.register(PatientFiles, PatientFilesAdmin)
admin.site.register(PeopleRelations, PeopleRelationsAdmin)
admin.site.register(NoteCategory, NoteCategoryAdmin)
admin.site.register(Notes, NotesAdmin)
admin.site.register(SORelations, SORelationsAdmin)
admin.site.register(SampleOrderRel, SampleOrderRelAdmin)
admin.site.register(FamilyRole, FamilyRoleAdmin)
admin.site.register(AffectedStatus, AffectedStatusAdmin)