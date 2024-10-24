# forms.py
from django import forms
from .models import Setting, SSHKey

class SettingForm(forms.ModelForm):
    class Meta:
        model = Setting
        fields = ['name', 'value', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'value': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

class SSHKeyForm(forms.ModelForm):
    class Meta:
        model = SSHKey
        fields = ['private_key', 'public_key']
        widgets = {
            'private_key': forms.FileInput(attrs={'class': 'form-control'}),
            'public_key': forms.FileInput(attrs={'class': 'form-control'}),
        }
