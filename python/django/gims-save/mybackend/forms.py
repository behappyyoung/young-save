from django import forms
from .models import MiscMessage


class MiscMessageForm(forms.ModelForm):

    class Meta:
        model = MiscMessage
        fields = '__all__'


class ManagerMessageForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = MiscMessage
        fields = ('title', 'content', 'date')
        widgets = {
            'date': forms.TextInput(attrs={'readonly': 'readonly'})
        }

