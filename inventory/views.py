from django.shortcuts import render, redirect
from .models import Environment, Group, Host, SSHConnectionHistory
from .forms import EnvironmentForm, GroupForm, HostForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
import subprocess
import logging


# Vistas de Ambientes
@login_required
def list_environments(request):
    environments = Environment.objects.all()
    return render(request, 'inventory/list_environments.html', {'environments': environments})

@login_required
def create_environment(request):
    form = EnvironmentForm()
    if request.method == 'POST':
        form = EnvironmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_environments')
    return render(request, 'inventory/create_environment.html', {'form': form})

@login_required
def edit_environment(request, pk):
    environment = Environment.objects.get(id=pk)
    form = EnvironmentForm(instance=environment)
    if request.method == 'POST':
        form = EnvironmentForm(request.POST, instance=environment)
        if form.is_valid():
            form.save()
            return redirect('list_environments')
    return render(request, 'inventory/edit_environment.html', {'form': form})

# Vistas de Grupos
@login_required
def list_groups(request):
    groups = Group.objects.all()
    return render(request, 'inventory/list_groups.html', {'groups': groups})

@login_required
def create_group(request):
    form = GroupForm()
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_groups')
    return render(request, 'inventory/create_group.html', {'form': form})

@login_required
def edit_group(request, pk):
    group = Group.objects.get(id=pk)
    form = GroupForm(instance=group)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('list_groups')
    return render(request, 'inventory/edit_group.html', {'form': form})

def delete_group(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        group.delete()
        messages.success(request, f"Grupo '{group.name}' eliminado exitosamente.")
        return redirect('list_groups')
    return redirect('list_groups')

# Vistas de Hosts
@login_required
def list_hosts(request):
    hosts = Host.objects.all()
    return render(request, 'inventory/list_hosts.html', {'hosts': hosts})

logger = logging.getLogger(__name__)

@login_required
def create_host(request):
    if request.method == 'POST':
        form = HostForm(request.POST)  # El formulario se llena con los datos del POST
        if form.is_valid():
            host = form.save(commit=False)  # Guarda el formulario, pero aún no lo almacena en la BD

            # Validar la conexión SSH antes de guardar definitivamente
            if validate_ssh_connection(host):
                host.save()  # Guarda el host solo si la conexión fue exitosa
                return render(request, 'inventory/success_template.html')  # Redirige a la página de éxito
            else:
                return render(request, 'inventory/error_template.html', {
                    'form': form,
                    'error_message': 'No se pudo conectar al host. Verifica los detalles e intenta nuevamente.'
                })  # Vuelve a mostrar el formulario con el error de conexión
    else:
        form = HostForm()  # Si no es POST, simplemente muestra el formulario vacío

    return render(request, 'inventory/create_host.html', {'form': form})


@login_required
def edit_host(request, pk):
    host = Host.objects.get(id=pk)
    form = HostForm(instance=host)
    if request.method == 'POST':
        form = HostForm(request.POST, instance=host)
        if form.is_valid():
            form.save()
            return redirect('list_hosts')
    return render(request, 'inventory/edit_host.html', {'form': form})

def delete_host(request, pk):
    host = get_object_or_404(Host, pk=pk)
    
    if request.method == 'POST':
        host.delete()
        messages.success(request, 'Host eliminado exitosamente.')
        return redirect('list_hosts')
    
    return render(request, 'inventory/confirm_delete_host.html', {'host': host})


# Lógica para Validación SSH


def validate_ssh_connection(host):
    """
    Ejecuta el script Bash para validar la conexión SSH pasando la IP o el hostname como argumento.
    """
    username = host.ansible_user  # El usuario ansible del host
    hostname = host.hostname  # El hostname o IP del host remoto
    script_path = "/opt/site/horeb/script.sh"  # Ruta completa de tu script Bash

    try:
        # Llamar al script Bash y pasar el hostname como argumento
        result = subprocess.call(['bash', script_path, username, hostname])

        # Verificar el resultado de la ejecución
        if result == 0:
            print("Conexión SSH exitosa.")
            return True
        else:
            print("Error al conectar vía SSH.")
            return False

    except Exception as e:
        print(f"Error al ejecutar el script: {e}")
        return False



@login_required
def success_view(request):
    return render(request, 'inventory/success_template.html')  # Cambia a tu plantilla de éxito

@login_required
def error_view(request):
    return render(request, 'inventory/error_template.html')  # Cambia a tu plantilla de error


###############################################




