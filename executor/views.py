from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
import subprocess
import tempfile
import os
import logging

from .forms import ExecutePlaybookHostForm, ExecutePlaybookGroupForm
from .models import ExecutionHistory
from inventory.models import Environment, Group, Host
from playbook.models import Playbook
from django.conf import settings

logger = logging.getLogger(__name__)

# ====================================================================
# Sección 1: Clase base para la ejecución de playbooks
# ====================================================================

class BasePlaybookExecuteView(View):
    """
    Clase base para la ejecución de playbooks en hosts individuales y grupos.
    """

    def execute_playbook(self, playbook, hosts, target_name=None, target_type='host'):
        """
        Ejecuta un playbook en uno o varios hosts o en un grupo.
        """
        inventory_path = None
        try:
            # Crear contenido del inventario
            inventory_content = self._generate_inventory_content(hosts, target_name)

            # Crear archivo temporal de inventario
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_inventory:
                temp_inventory.write(inventory_content)
                inventory_path = temp_inventory.name

            # Construir el comando de Ansible
            ansible_command = self._build_ansible_command(playbook, inventory_path, target_name or hosts[0].ansible_host, target_type)

            # Ejecutar el comando
            result = subprocess.run(
                ansible_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Registrar las salidas
            logger.debug(f"Salida estándar: {result.stdout}")
            logger.debug(f"Error estándar: {result.stderr}")

            if result.returncode != 0:
                logger.error(f"Ejecución del playbook fallida con código de retorno {result.returncode}")
                return result.stderr, 'Failure'
            else:
                return result.stdout, 'Success'

        except Exception as e:
            logger.exception("Ocurrió un error inesperado durante la ejecución del playbook.")
            return str(e), 'Failure'
        finally:
            if inventory_path and os.path.exists(inventory_path):
                os.remove(inventory_path)


    def _generate_inventory_content(self, hosts, group_name=None):
        """
        Genera el contenido del inventario para un host o grupo.
        """
        inventory_content = f"[{group_name}]\n" if group_name else ""
        for host in hosts:
            ssh_key_path = host.ssh_key
            inventory_content += (
                f"{host.ansible_host} "
                f"ansible_user={host.ansible_user} "
                f"ansible_ssh_private_key_file={ssh_key_path} "
                f"ansible_python_interpreter={host.python_interpreter}\n"
            )
        return inventory_content

    def _build_ansible_command(self, playbook, inventory_path, limit_value, target_type=None):
        """
        Construye el comando de Ansible para ejecutar un playbook.
        target_type puede ser 'host' o 'group'.
        """
        ansible_command = [
            'ansible-playbook',
            '-i', inventory_path,
            playbook.playbook_file.path,
            '--limit', limit_value
        ]

        # Determinar si estamos ejecutando en un host o en un grupo
        if target_type == 'host':
            ansible_command.extend(['-e', f'host={limit_value}'])
        elif target_type == 'group':
            ansible_command.extend(['-e', f'group={limit_value}'])

        # Registrar el comando para depuración
        logger.debug(f"Ejecutando comando: {' '.join(ansible_command)}")

        return ansible_command

    
    
    def _save_execution_history(self, request, form, playbook, output, status):
        """
        Guarda el historial de ejecución.
        """
        return ExecutionHistory.objects.create(
            playbook=playbook,
            environment=form.cleaned_data['environment'],
            group=form.cleaned_data['group'],
            host=form.cleaned_data.get('host'),  # El host puede ser None si es por grupo
            executed_by=request.user,
            output=output,
            status=status
        )
    
    def _display_execution_message(self, request, target_name, status, output):
        """
        Muestra un mensaje al usuario dependiendo del resultado de la ejecución.
        """
        if status == 'Success':
            messages.success(request, f'Playbook ejecutado exitosamente en {target_name}.')
        else:
            messages.error(request, f'Error al ejecutar el playbook en {target_name}: {output}')

# ====================================================================
# Sección 2: Ejecución de playbooks en un Host
# ====================================================================

@method_decorator(login_required, name='dispatch')
class PlaybookExecuteView(BasePlaybookExecuteView):
    """
    Vista para ejecutar playbooks en un host específico.
    """
    def get(self, request):
        form = ExecutePlaybookHostForm()
        return render(request, 'executor/playbook_execute.html', {'form': form})

    def post(self, request):
        form = ExecutePlaybookHostForm(request.POST)
        if form.is_valid():
            host = form.cleaned_data['host']
            playbook = form.cleaned_data['playbook']

            # Ejecutar el playbook en el host, asegurándonos de pasar el tipo 'host'
            output, status = self.execute_playbook(playbook, [host], target_name=host.ansible_host, target_type='host')

            # Guardar en el historial
            execution = self._save_execution_history(request, form, playbook, output, status)

            # Mostrar mensaje al usuario
            self._display_execution_message(request, host.hostname, status, output)
            return redirect('executor:execution_detail', pk=execution.pk)
        return render(request, 'executor/playbook_execute.html', {'form': form})


    def _save_execution_history(self, request, form, playbook, output, status):
        """
        Guarda el historial de ejecución.
        """
        return ExecutionHistory.objects.create(
            playbook=playbook,
            environment=form.cleaned_data['environment'],
            group=form.cleaned_data['group'],
            host=form.cleaned_data['host'],
            executed_by=request.user,
            output=output,
            status=status
        )

    def _display_execution_message(self, request, hostname, status, output):
        """
        Muestra un mensaje al usuario dependiendo del resultado de la ejecución.
        """
        if status == 'Success':
            messages.success(request, f'Playbook ejecutado exitosamente en {hostname}.')
        else:
            messages.error(request, f'Error al ejecutar el playbook en {hostname}: {output}')


# ====================================================================
# Sección 3: Ejecución de playbooks en un Grupo
# ====================================================================

@method_decorator(login_required, name='dispatch')
class ExecutePlaybookGroupView(BasePlaybookExecuteView):
    """
    Vista para ejecutar playbooks en un grupo de hosts.
    """
    def get(self, request):
        form = ExecutePlaybookGroupForm()
        return render(request, 'executor/playbook_execute_group.html', {'form': form})

    def post(self, request):
        form = ExecutePlaybookGroupForm(request.POST)
        if form.is_valid():
            group = form.cleaned_data['group']
            playbook = form.cleaned_data['playbook']
            hosts = group.host_set.all()

            # Ejecutar el playbook en el grupo, pasando el nombre del grupo y el tipo 'group'
            output, status = self.execute_playbook(playbook, hosts, target_name=group.name, target_type='group')

            # Guardar en el historial
            execution = self._save_execution_history(request, form, playbook, output, status)

            # Mostrar mensaje al usuario
            self._display_execution_message(request, group.name, status, output)
            return redirect('executor:execution_detail', pk=execution.pk)
        return render(request, 'executor/playbook_execute_group.html', {'form': form})



# ====================================================================
# Sección 4: Vistas auxiliares para cargar datos dinámicos
# ====================================================================

class LoadHostsView(View):
    """
    Vista para cargar hosts basados en el grupo seleccionado.
    """
    def get(self, request):
        group_id = request.GET.get('group_id')
        hosts = Host.objects.filter(group_id=group_id)
        data = [{'id': host.id, 'name': host.hostname} for host in hosts]
        return JsonResponse({'hosts': data})

class LoadGroupsView(View):
    """
    Vista para cargar grupos basados en el ambiente seleccionado.
    """
    def get(self, request):
        environment_id = request.GET.get('environment_id')
        groups = Group.objects.filter(environment_id=environment_id)
        data = [{'id': group.id, 'name': group.name} for group in groups]
        return JsonResponse({'groups': data})

class LoadPlaybooksView(View):
    """
    Vista para cargar playbooks basados en el tipo y sistema operativo o grupo.
    """
    def get(self, request):
        playbook_type = request.GET.get('playbook_type')
        playbooks = self._get_playbooks(playbook_type, request)
        data = [{'id': pb.id, 'name': pb.name} for pb in playbooks]
        return JsonResponse({'playbooks': data})

    def _get_playbooks(self, playbook_type, request):
        """
        Obtiene los playbooks filtrados por tipo y otros parámetros.
        """
        if playbook_type == 'host':
            operating_system = request.GET.get('operating_system')
            return Playbook.objects.filter(playbook_type='host', operating_system__iexact=operating_system.strip())
        elif playbook_type == 'group':
            group_id = request.GET.get('group_id')
            group = get_object_or_404(Group, pk=group_id)
            operating_systems = group.host_set.values_list('operating_system', flat=True).distinct()
            return Playbook.objects.filter(playbook_type='group', operating_system__in=operating_systems)
        return Playbook.objects.none()

# ====================================================================
# Sección 5: Historial de ejecuciones y detalles
# ====================================================================

@login_required
def execution_history(request):
    """
    Vista para mostrar el historial de ejecuciones con paginación.
    """
    history_list = ExecutionHistory.objects.all().order_by('-date')
    paginator = Paginator(history_list, 10)  # Mostrar 10 ejecuciones por página
    page_number = request.GET.get('page')
    history = paginator.get_page(page_number)
    return render(request, 'executor/execution_history.html', {'history': history})

@login_required
def execution_detail(request, pk):
    """
    Vista para mostrar los detalles de una ejecución específica.
    """
    execution = get_object_or_404(ExecutionHistory, pk=pk)
    return render(request, 'executor/execution_detail.html', {'execution': execution})
