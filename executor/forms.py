from django import forms
from inventory.models import Environment, Group, Host
from playbook.models import Playbook

class ExecutePlaybookHostForm(forms.Form):
    environment = forms.ModelChoiceField(queryset=Environment.objects.all(), label='Ambiente')
    group = forms.ModelChoiceField(queryset=Group.objects.none(), label='Grupo')
    host = forms.ModelChoiceField(queryset=Host.objects.none(), label='Host')
    playbook = forms.ModelChoiceField(queryset=Playbook.objects.none(), label='Playbook')

    def __init__(self, *args, **kwargs):
        super(ExecutePlaybookHostForm, self).__init__(*args, **kwargs)

        if 'environment' in self.data:
            try:
                environment_id = int(self.data.get('environment'))
                self.fields['group'].queryset = Group.objects.filter(environment_id=environment_id)
            except (ValueError, TypeError):
                pass
        elif self.initial.get('environment'):
            environment_id = self.initial.get('environment').id
            self.fields['group'].queryset = Group.objects.filter(environment_id=environment_id)
        else:
            self.fields['group'].queryset = Group.objects.none()

        if 'group' in self.data:
            try:
                group_id = int(self.data.get('group'))
                self.fields['host'].queryset = Host.objects.filter(group_id=group_id)
            except (ValueError, TypeError):
                pass
        elif self.initial.get('group'):
            group_id = self.initial.get('group').id
            self.fields['host'].queryset = Host.objects.filter(group_id=group_id)
        else:
            self.fields['host'].queryset = Host.objects.none()

        if 'host' in self.data:
            try:
                host_id = int(self.data.get('host'))
                host = Host.objects.get(id=host_id)
                operating_system = host.operating_system
                self.fields['playbook'].queryset = Playbook.objects.filter(
                    playbook_type='host',
                    operating_system__iexact=operating_system
                )
            except (ValueError, TypeError, Host.DoesNotExist):
                pass
        elif self.initial.get('host'):
            host = self.initial.get('host')
            operating_system = host.operating_system
            self.fields['playbook'].queryset = Playbook.objects.filter(
                playbook_type='host',
                operating_system__iexact=operating_system
            )
        else:
            self.fields['playbook'].queryset = Playbook.objects.none()

        # Incluir los valores seleccionados en los queryset para evitar errores de validación
        if self.is_bound:
            group = self.fields['group'].queryset.filter(pk=self.data.get('group')).first()
            if group:
                self.fields['group'].queryset = Group.objects.filter(pk=group.pk)
            host = self.fields['host'].queryset.filter(pk=self.data.get('host')).first()
            if host:
                self.fields['host'].queryset = Host.objects.filter(pk=host.pk)
            playbook = self.fields['playbook'].queryset.filter(pk=self.data.get('playbook')).first()
            if playbook:
                self.fields['playbook'].queryset = Playbook.objects.filter(pk=playbook.pk)

class ExecutePlaybookGroupForm(forms.Form):
    environment = forms.ModelChoiceField(queryset=Environment.objects.all(), label='Ambiente')
    group = forms.ModelChoiceField(queryset=Group.objects.none(), label='Grupo')
    playbook = forms.ModelChoiceField(queryset=Playbook.objects.none(), label='Playbook')

    def __init__(self, *args, **kwargs):
        super(ExecutePlaybookGroupForm, self).__init__(*args, **kwargs)

        if 'environment' in self.data:
            try:
                environment_id = int(self.data.get('environment'))
                self.fields['group'].queryset = Group.objects.filter(environment_id=environment_id)
            except (ValueError, TypeError):
                pass
        elif self.initial.get('environment'):
            environment_id = self.initial.get('environment').id
            self.fields['group'].queryset = Group.objects.filter(environment_id=environment_id)
        else:
            self.fields['group'].queryset = Group.objects.none()

        if 'group' in self.data:
            try:
                group_id = int(self.data.get('group'))
                group = Group.objects.get(id=group_id)
                operating_systems = group.host_set.values_list('operating_system', flat=True).distinct()

                # Recargar los playbooks según el sistema operativo de los hosts del grupo
                self.fields['playbook'].queryset = Playbook.objects.filter(
                    playbook_type='group',
                    operating_system__in=operating_systems
                )
            except (ValueError, TypeError, Group.DoesNotExist):
                pass
        elif self.initial.get('group'):
            group = self.initial.get('group')
            operating_systems = group.host_set.values_list('operating_system', flat=True).distinct()

            # Recargar el queryset de playbooks si el grupo ya está en los datos iniciales
            self.fields['playbook'].queryset = Playbook.objects.filter(
                playbook_type='group',
                operating_system__in=operating_systems
            )
        else:
            self.fields['playbook'].queryset = Playbook.objects.none()

        # Asegurarnos de que el `playbook` seleccionado está en el `queryset`
        if self.is_bound:
            playbook_id = self.data.get('playbook')
            if playbook_id:
                self.fields['playbook'].queryset = Playbook.objects.filter(pk=playbook_id)

