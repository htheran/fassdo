
# Create your views here.
from django.shortcuts import render, redirect
from .forms import ServiceManagerForm, SettingForm, SSHKeyForm

def manage_settings(request):
    selected_option = None
    form = ServiceManagerForm(request.POST or None)
    setting_form = None
    ssh_form = None

    if form.is_valid():
        selected_option = form.cleaned_data.get('option')
        if selected_option == 'variable':
            setting_form = SettingForm(request.POST)
            if setting_form.is_valid():
                setting_form.save()
                return redirect('manage_settings')
        elif selected_option == 'ssh':
            ssh_form = SSHKeyForm(request.POST, request.FILES)
            if ssh_form.is_valid():
                ssh_form.save()
                return redirect('manage_settings')

    return render(request, 'settings/manage_settings.html', {
        'form': form,
        'setting_form': setting_form,
        'ssh_form': ssh_form,
        'selected_option': selected_option
    })
