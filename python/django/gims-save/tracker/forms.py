from django import forms
from tracker.models import Samples, Orders, SampleOrderRel, OrderGeneList, Notes, \
    PatientRelations,Patients, Family, OrderGroups, PatientFiles
from users.models import UserProfile
from mybackend.models import GeneLists
from django.forms.widgets import Select
import itertools


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patients
        fields =  '__all__'
        widgets={
            'pid': forms.TextInput(attrs={'readonly': 'readonly'}),
            'mrn': forms.TextInput(attrs={'readonly': 'readonly'}),
            'sex': forms.TextInput(attrs={'readonly': 'readonly'}),
            'memo': forms.Textarea(),
        }


class SampleForm(forms.ModelForm):
    class Meta:
        model = Samples
        fields = ['asn', 'patient_id', 'type', 'status', 'volume', 'note']
        widgets = {
            'patient_id': forms.TextInput(attrs={'readonly': 'readonly'}),
            'type': forms.TextInput(attrs={'readonly': 'readonly'}),
            'asn': forms.TextInput(attrs={'readonly': 'readonly'})
        }


class OrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        try:
            CHOICES = UserProfile.objects.filter(role='Interpretation')
        except:
            CHOICES = []
        self.fields['owner'].widget = forms.Select(choices=((x.id, x.username) for x in CHOICES))
        # self.fields['secondary_findings_flag'].initial = False

    class Meta:
        model = Orders
        fields = '__all__'
        labels = {'desc': ' Memo / Desc ', 'secondary_findings_flag' : 'Provide Secondary Findings'}
        widgets = {
            'patient_id': forms.TextInput(attrs={'readonly': 'readonly'}),
            'order_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'order_date': forms.TextInput(attrs={'readonly': 'readonly'}),
            'due_date': forms.TextInput(attrs={'readonly': 'readonly'}),
            'lab_status': forms.TextInput(attrs={'readonly': 'readonly'}),
            'complete_date': forms.TextInput(attrs={'readonly': 'readonly'}),
            'updated': forms.TextInput(attrs={'readonly': 'readonly'}),
            'physician_phenotype': forms.Textarea(attrs={'readonly': 'readonly'}),
            'physician_genelist': forms.Textarea(attrs={'readonly': 'readonly'}),
            'phenotype': forms.Textarea(),
            'genelist': forms.Textarea(),
            # 'secondary_findings_note': forms.Textarea(),
            'secondary_findings_flag':forms.Select(choices=(('', 'Not Selected'), ('Yes', 'Yes'), ('No', 'No')))
        }


class OrderGroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(OrderGroupForm, self).__init__(*args, **kwargs)

        try:
            CHOICES = Orders.objects.all()
        except:
            CHOICES = []
        self.fields['order'].widget = forms.Select(choices=((x.id, x.order_name) for x in CHOICES))

    class Meta:
        model = OrderGroups
        fields = ['group_id', 'order', 'relation', 'affectedstatus', 'desc']
        widgets={
            'desc': forms.Textarea(),
        }


class PatientRelationsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PatientRelationsForm, self).__init__(*args, **kwargs)

        try:
            CHOICES = Patients.objects.all().values('pid', 'first_name', 'middle_name', 'last_name', 'mrn')
        except:
            CHOICES = []

        self.fields['relative'].widget = forms.Select(choices=((x['pid'], x['first_name'] + ' ' + (x['middle_name'] or '') + ' ' + x['last_name'] + ' ( ' + x['mrn']+ ' ) ') for x in CHOICES))

    class Meta:
        model = PatientRelations
        fields = '__all__'
        widgets = {
            'main': forms.TextInput(attrs={'readonly': 'readonly'}),
        }


class PatientFilesForm(forms.ModelForm):
    class Meta:
        model = PatientFiles
        fields = ['patient', 'file_title', 'desc', 'file', 'file_name', 'type']
        widgets = {
            'patient': forms.TextInput(attrs={'type': 'hidden'}),
            'file_name': forms.TextInput(attrs={'placeholder': 'it will replace the original file name ( with same extention )'})
        }


class FamilyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FamilyForm, self).__init__(*args, **kwargs)

        try:
            CHOICES = Patients.objects.all().values('id', 'first_name', 'middle_name', 'last_name', 'mrn')
        except:
            CHOICES = []

        self.fields['patient'].widget = forms.Select(
        choices=((x['id'], x['first_name'] + ' ' + (x['middle_name'] or '') + ' ' + x['last_name'] + ' ( ' + x['mrn'] + ' ) ')
                 for x in CHOICES))

    class Meta:
        model = Family
        fields = ('family_id', 'role', 'affectedstatus', 'patient')
        widgets={
            'family_id' : forms.TextInput(attrs={'readonly': 'readonly'}),
        }


class PatientRelationsEditForm(forms.ModelForm):

    class Meta:

        model = PatientRelations
        fields = '__all__'
        widgets={
            'main': forms.TextInput(attrs={'readonly': 'readonly'}),
            'relative': forms.TextInput(attrs={'readonly': 'readonly'}),

        }


class SampleOrderRelForm(forms.ModelForm):
    class Meta:
        model = SampleOrderRel
        fields = '__all__'


class OrderGeneListForm(forms.ModelForm):
    class Meta:
        model = OrderGeneList
        fields = '__all__'


class GeneListsForm(forms.ModelForm):
    class Meta:
        model = GeneLists
        fields = ('category', 'name','list', 'desc')


class NotesPatientForm(forms.ModelForm):
    # def __init__(self, patient = None, *args, **kwargs):
    #     print(patient)
    #     super(NotesPatientForm, self).__init__(*args, **kwargs)
    #     print(patient)

    #   removed recipients for now
    #     try:
    #         CHOICES = UserProfile.objects.all()
    #     except:
    #         CHOICES = []
    #     self.fields['recipients'].widget = forms.SelectMultiple(
    #             choices=itertools.chain(((x.user_id, x.username) for x in CHOICES)))

    class Meta:
        model = Notes
        fields = ('patient', 'category', 'order',  'note')

        widgets = {
            'update_time': forms.TextInput(attrs={'readonly': 'readonly'}),
            'patient': forms.TextInput(attrs={'readonly': 'readonly'})
        }


class NotesOrderForm(forms.ModelForm):

    class Meta:
        model = Notes
        fields = ('order', 'patient', 'category',  'note')
        widgets = {
                'order': forms.Select(attrs={'disabled': 'disabled'}),
                'update_time': forms.TextInput(attrs={'readonly': 'readonly'}),
                'patient': forms.TextInput(attrs={'readonly': 'readonly'})
            }