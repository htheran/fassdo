from django import forms
from .models import Setting, SSHKey

class ServiceManagerForm(forms.Form):
    option = forms.ChoiceField(
        choices=[('variable', 'Guardar Variable'), ('ssh', 'Subir Llave SSH')],
        widget=forms.Select(attrs={'class': 'form-control', 'onchange': 'this.form.submit();'}),
        label="Opciones"
    )

class SettingForm(forms.ModelForm):
    class Meta:
        model = Setting
        fields = ['key', 'value', 'description']
        widgets = {
            'key': forms.TextInput(attrs={'class': 'form-control'}),
            'value': forms.Textarea(attrs={'class': 'form-control'}),
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
