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


class NotesForm(forms.ModelForm):
    class Meta:
        CHOICES = UserProfile.objects.all()
        model = Notes
        fields = ('order', 'category','recipient', 'update_time', 'note', 'patient_id')
        widgets = {
            'recipient': Select(choices=itertools.chain( ((x.user_id, x.username) for x in CHOICES) , [("",'None')])),
            'update_time': forms.TextInput(attrs={'readonly': 'readonly'}),
            'patient_id': forms.TextInput(attrs={'readonly': 'readonly'})
        }


class NotesOrderForm(forms.ModelForm):
    class Meta:
        CHOICES = UserProfile.objects.all()
        model = Notes
        fields = ('order', 'category','recipient', 'update_time', 'note', 'patient_id')
        widgets = {
            'order': forms.Select(attrs={'disabled': 'disabled'}),
            'recipient': Select(choices=itertools.chain( ((x.user_id, x.username) for x in CHOICES) , [("",'None')])),
            'update_time': forms.TextInput(attrs={'readonly': 'readonly'}),
            'patient_id': forms.TextInput(attrs={'readonly': 'readonly'})
        }