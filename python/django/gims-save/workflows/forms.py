
from django import forms
from .models import Workflows


class WorkflowsForm(forms.ModelForm):
    workflow_id = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    inputs = forms.CharField(widget=forms.Textarea)
    fixed_inputs = forms.CharField(widget=forms.Textarea)
    desc = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Workflows
        fields = '__all__'