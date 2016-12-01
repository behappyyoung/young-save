from django import forms
from tracker.models import Samples, Orders, SampleOrderRel, PatientOrderPhenoType, PhenoTypes, OrderGeneList, Notes, PatientRelations,Patients
from users.models import UserProfile
from mybackend.models import GeneLists
from django.forms.widgets import Select
import itertools


class OrderForm(forms.ModelForm):
    class Meta:
        CHOICES = UserProfile.objects.filter(role='Interpretation')
        model = Orders
        fields =  '__all__'
        # fields = ('order_name', 'status', 'phenotype', 'owner')
        widgets={
            'patient_id': forms.TextInput(attrs={'readonly': 'readonly'}),
            'order_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'order_date': forms.TextInput(attrs={'readonly': 'readonly'}),
            'due_date': forms.TextInput(attrs={'readonly': 'readonly'}),
            'complete_date': forms.TextInput(attrs={'readonly': 'readonly'}),
            'updated': forms.TextInput(attrs={'readonly': 'readonly'}),
            'owner':  Select(choices=( (x.id, x.username) for x in CHOICES )),
            'phenotype': forms.Textarea(),
        }


class PatientRelationsForm(forms.ModelForm):
    class Meta:
        CHOICES = Patients.objects.all()
        model = PatientRelations
        fields = '__all__'
        widgets={
            'relative': Select(choices=( (x.pid, x.first_name + ' '+  x.last_name + ' ( MRN : ' + x.mrn + ' ) ') for x in CHOICES )),
        }


class PatientRelationsEditForm(forms.ModelForm):
    class Meta:
        CHOICES = Patients.objects.all()
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


class PatientOrderPhenoTypeForm(forms.ModelForm):
    class Meta:
        model = PatientOrderPhenoType
        fields = '__all__'


class PhenoTypesForm(forms.ModelForm):
    desc = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = PhenoTypes
        fields = ('name', 'type', 'desc', 'image', 'date',)
        widgets = {
            'date': forms.TextInput(attrs={'readonly': 'readonly'})
        }


class OrderGeneListForm(forms.ModelForm):
    class Meta:
        model = OrderGeneList
        fields = '__all__'


class GeneListsForm(forms.ModelForm):
    class Meta:
        model = GeneLists
        fields = ('category', 'name','list', 'desc')


class NotesPatientForm(forms.ModelForm):
    class Meta:
        CHOICES = UserProfile.objects.all()
        model = Notes
        fields = ('patient_id', 'category','recipients', 'update_time', 'note')
        widgets = {
            'recipients': forms.SelectMultiple(
                choices=itertools.chain(((x.user_id, x.username) for x in CHOICES))),
            'update_time': forms.TextInput(attrs={'readonly': 'readonly'}),
            'patient_id': forms.TextInput(attrs={'readonly': 'readonly'})
        }


class NotesOrderForm(forms.ModelForm):
    class Meta:
        CHOICES = UserProfile.objects.all()
        model = Notes
        fields = ('order', 'patient_id', 'category', 'recipients', 'note', 'update_time')
        widgets = {
            'order': forms.Select(attrs={'disabled': 'disabled'}),
            'recipients': forms.SelectMultiple(
                choices=itertools.chain(((x.user_id, x.username) for x in CHOICES))),
            'update_time': forms.TextInput(attrs={'readonly': 'readonly'}),
            'patient_id': forms.TextInput(attrs={'readonly': 'readonly'})
        }