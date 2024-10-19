from django import forms
from .models import Playbook

class PlaybookForm(forms.ModelForm):
    class Meta:
        model = Playbook
        fields = ['name', 'description', 'playbook_file', 'playbook_type', 'operating_system']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter playbook name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter playbook description'}),
            'playbook_file': forms.FileInput(attrs={'class': 'form-control'}),
            'playbook_type': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'operating_system': forms.Select(attrs={'class': 'form-select'}),
        }
