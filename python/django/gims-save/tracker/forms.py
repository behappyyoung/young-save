from django import forms
from tracker.models import Samples, Orders, SampleOrderRel, PatientOrderPhenoType, PhenoTypes, OrderGeneList, Notes, \
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
			# 'ethnicity': forms.TextInput(attrs={'readonly': 'readonly'}),
			'sex': forms.TextInput(attrs={'readonly': 'readonly'}),
			'memo': forms.Textarea(),
		}


class OrderForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(OrderForm, self).__init__(*args, **kwargs)
		try:
			CHOICES = UserProfile.objects.filter(role='Interpretation')
		except:
			CHOICES = []
		self.fields['owner'].widget = forms.Select(choices=((x.user_id, x.username) for x in CHOICES))

	class Meta:
		model = Orders
		fields = '__all__'
		labels = {'desc': ' Memo / Desc '}
		widgets = {
			'patient_id': forms.TextInput(attrs={'readonly': 'readonly'}),
			'order_name': forms.TextInput(attrs={'readonly': 'readonly'}),
			'order_date': forms.TextInput(attrs={'readonly': 'readonly'}),
			'due_date': forms.TextInput(attrs={'readonly': 'readonly'}),
			'complete_date': forms.TextInput(attrs={'readonly': 'readonly'}),
			'updated': forms.TextInput(attrs={'readonly': 'readonly'}),
			'physician_phenotype': forms.TextInput(attrs={'readonly': 'readonly'}),
			'phenotype': forms.Textarea(),
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
		fields = ['group_id', 'order', 'relation', 'affected_status', 'desc']
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

		self.fields['relative'].widget = forms.Select(choices=((x['pid'], x['first_name'] + ' ' + x['middle_name'] + ' ' + x['last_name'] + ' ( ' + x['mrn']+ ' ) ') for x in CHOICES))
	class Meta:
		model = PatientRelations
		fields = '__all__'
		widgets = {
			'main': forms.TextInput(attrs={'readonly': 'readonly'}),
		}


class PatientFilesForm(forms.ModelForm):
	class Meta:
		model = PatientFiles
		fields = ['patient', 'file_title', 'desc', 'file', 'type']
		widgets = {
			'patient': forms.TextInput(attrs={'type': 'hidden'}),
		}


class FamilyForm(forms.ModelForm):


	class Meta:
		model = Family
		fields = '__all__'
		widgets={
			# 'family_id' : forms.TextInput(attrs={'readonly': 'readonly'}),
			# 'patient': Select(choices=((x.pid, x.first_name + ' ' + x.last_name + ' ( MRN : ' + x.mrn + ' ) ') for x in CHOICES )),
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
	def __init__(self, *args, **kwargs):
		super(NotesPatientForm, self).__init__(*args, **kwargs)
		try:
			CHOICES = UserProfile.objects.all()
		except:
			CHOICES = []
		self.fields['recipients'].widget = forms.SelectMultiple(
				choices=itertools.chain(((x.user_id, x.username) for x in CHOICES)))

	class Meta:
		model = Notes
		fields = ('patient_id', 'category','recipients', 'update_time', 'note')

		widgets = {
			'update_time': forms.TextInput(attrs={'readonly': 'readonly'}),
			'patient_id': forms.TextInput(attrs={'readonly': 'readonly'})
		}


class NotesOrderForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(NotesOrderForm, self).__init__(*args, **kwargs)
		try:
			CHOICES = UserProfile.objects.all()
		except:
			CHOICES = []
		self.fields['recipients'].widget = forms.SelectMultiple(
			choices=itertools.chain(((x.user_id, x.username) for x in CHOICES)))
	class Meta:
		model = Notes
		fields = ('order', 'patient_id', 'category', 'recipients', 'note', 'update_time')
		widgets = {
				'order': forms.Select(attrs={'disabled': 'disabled'}),
				'update_time': forms.TextInput(attrs={'readonly': 'readonly'}),
				'patient_id': forms.TextInput(attrs={'readonly': 'readonly'})
			}