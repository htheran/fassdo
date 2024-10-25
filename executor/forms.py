from django import forms
from inventory.models import Environment, Group, Host
from playbook.models import Playbook

# service_manager/forms.py


class ExecutePlaybookHostForm(forms.Form):
    environment = forms.ModelChoiceField(
        queryset=Environment.objects.all(),
        label='Ambiente',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'onchange': 'this.form.submit();'})
    )
    group = forms.ModelChoiceField(
        queryset=Group.objects.none(),
        label='Grupo',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'onchange': 'this.form.submit();'})
    )
    host = forms.ModelChoiceField(
        queryset=Host.objects.none(),
        label='Host',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    playbook = forms.ModelChoiceField(
        queryset=Playbook.objects.filter(playbook_type='host'),
        label='Playbook',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super(ExecutePlaybookHostForm, self).__init__(*args, **kwargs)

        if 'environment' in self.data:
            try:
                environment_id = int(self.data.get('environment'))
                self.fields['group'].queryset = Group.objects.filter(environment_id=environment_id)
            except (ValueError, TypeError):
                pass

        if 'group' in self.data:
            try:
                group_id = int(self.data.get('group'))
                self.fields['host'].queryset = Host.objects.filter(group_id=group_id)
            except (ValueError, TypeError):
                pass

        # Cargar siempre los playbooks de tipo 'host'
        self.fields['playbook'].queryset = Playbook.objects.filter(playbook_type='host')


########################################

class ExecutePlaybookGroupForm(forms.Form):
    environment = forms.ModelChoiceField(
        queryset=Environment.objects.all(),
        label='Ambiente',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'onchange': 'this.form.submit();'})
    )
    group = forms.ModelChoiceField(
        queryset=Group.objects.none(),
        label='Grupo',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'onchange': 'this.form.submit();'})
    )
    playbook = forms.ModelChoiceField(
        queryset=Playbook.objects.filter(playbook_type='group'),  # Aquí listamos todos los playbooks de tipo 'group'
        label='Playbook',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super(ExecutePlaybookGroupForm, self).__init__(*args, **kwargs)

        # Solo cargar grupos si se ha seleccionado un environment válido
        if 'environment' in self.data and self.data.get('environment').isdigit():
            try:
                environment_id = int(self.data.get('environment'))
                self.fields['group'].queryset = Group.objects.filter(environment_id=environment_id)
            except (ValueError, TypeError):
                self.fields['group'].queryset = Group.objects.none()

        # Listar todos los playbooks de tipo 'group' independientemente del grupo
        self.fields['playbook'].queryset = Playbook.objects.filter(playbook_type='group')

#####################################################################



class SchedulePlaybookHostForm(ExecutePlaybookHostForm):
    scheduled_date = forms.DateTimeField(
        label="Fecha y hora de ejecución",
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control', 
            'type': 'datetime-local'  # Importante: Este tipo permite seleccionar tanto fecha como hora
        }),
        required=True
    )

class SchedulePlaybookGroupForm(ExecutePlaybookGroupForm):
    scheduled_date = forms.DateTimeField(
        label="Fecha y hora de ejecución",
         widget=forms.DateTimeInput(attrs={
            'class': 'form-control', 
            'type': 'datetime-local'  # Importante: Este tipo permite seleccionar tanto fecha como hora
        }),
        required=True
    )
