from django import forms
from .models import Environment, Group, Host

class EnvironmentForm(forms.ModelForm):
    class Meta:
        model = Environment
        fields = ['name', 'description']

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description', 'environment']

class HostForm(forms.ModelForm):
    class Meta:
        model = Host
        fields = ['environment', 'group', 'hostname', 'ansible_host', 'ansible_user', 'operating_system', 'python_interpreter', 'ssh_key']
