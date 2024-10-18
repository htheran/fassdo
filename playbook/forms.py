from django import forms
from .models import Playbook


class PlaybookForm(forms.ModelForm):
    class Meta:
        model = Playbook
        fields = ['name', 'description', 'playbook_file', 'playbook_type', 'operating_system']

    playbook_type = forms.ChoiceField(choices=Playbook.PLAYBOOK_TYPE_CHOICES, widget=forms.RadioSelect)
    operating_system = forms.ChoiceField(choices=Playbook.OS_CHOICES, widget=forms.Select)

