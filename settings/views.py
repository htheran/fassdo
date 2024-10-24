from django.shortcuts import render

# Create your views here.
# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SettingForm, SSHKeyForm
from .models import Setting, SSHKey
from django.contrib import messages

# Manejar creación y edición
def manage_settings(request, setting_id=None):
    if setting_id:
        setting = get_object_or_404(Setting, id=setting_id)
        message_action = "editada"
    else:
        setting = None
        message_action = "creada"

    if request.method == 'POST':
        setting_form = SettingForm(request.POST, instance=setting)
        ssh_form = SSHKeyForm(request.POST, request.FILES)

        if setting_form.is_valid():
            setting_form.save()
            messages.success(request, f"Configuración {message_action} correctamente.")
            return redirect('manage_settings')

        if ssh_form.is_valid():
            ssh_form.save()
            messages.success(request, "Llaves SSH guardadas correctamente.")
            return redirect('manage_settings')
    
    else:
        setting_form = SettingForm(instance=setting)
        ssh_form = SSHKeyForm()

    settings = Setting.objects.all()

    context = {
        'setting_form': setting_form,
        'ssh_form': ssh_form,
        'settings': settings
    }

    return render(request, 'settings/manage_settings.html', context)

# Eliminar configuración
def delete_setting(request, setting_id):
    setting = get_object_or_404(Setting, id=setting_id)
    setting.delete()
    messages.success(request, "Configuración eliminada correctamente.")
    return redirect('manage_settings')
