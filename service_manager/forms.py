# service_manager/forms.py
from django import forms
from inventory.models import Environment, Group, Host

class HostStatusForm(forms.Form):
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

    def __init__(self, *args, **kwargs):
        super(HostStatusForm, self).__init__(*args, **kwargs)
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

# service_manager/forms.py

# service_manager/forms.py

class ServiceManagerForm(forms.Form):
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
    service_name = forms.ChoiceField(
        choices=[
            ('httpd', 'HTTPD'),
            ('firewalld', 'Firewalld'),
            ('nginx', 'Nginx'),
            ('vsftpd', 'Vsftpd'),
            ('mariadb', 'MariaDB'),
            ('postgresql', 'PostgreSQL'),
            ('NetworkManager', 'NetworkManager')
        ],
        label='Servicio',
        widget=forms.Select(attrs={'class': 'form-control'})  # Añade el estilo aquí
    )
    action = forms.ChoiceField(
        choices=[
            ('start', 'Iniciar'),
            ('stop', 'Detener'),
            ('restart', 'Reiniciar'),
            ('status', 'Estado')
        ],
        label='Acción',
        widget=forms.Select(attrs={'class': 'form-control'})  # Añade el estilo aquí
    )

    def __init__(self, *args, **kwargs):
        super(ServiceManagerForm, self).__init__(*args, **kwargs)
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
