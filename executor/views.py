# executor/views.py

from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from .forms import ExecutePlaybookHostForm, ExecutePlaybookGroupForm
from .models import ExecutionHistory
from inventory.models import Environment, Group, Host
from playbook.models import Playbook
from django.http import JsonResponse
import subprocess
import tempfile
import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class BasePlaybookExecuteView(View):
    def execute_playbook_on_host(self, playbook, host):
        inventory_path = None
        try:
            # Verificar que el archivo de clave SSH existe
            if not host.ssh_key:
                error_message = f"El host {host.hostname} no tiene una clave SSH asignada."
                logger.error(error_message)
                return error_message, 'Failure'
            ssh_key_path = host.ssh_key
            if not os.path.exists(ssh_key_path):
                error_message = f"La clave SSH no se encuentra en {ssh_key_path}"
                logger.error(error_message)
                return error_message, 'Failure'

            # Verificar que el playbook existe
            playbook_path = playbook.playbook_file.path
            if not os.path.exists(playbook_path):
                error_message = f"El playbook no se encuentra en {playbook_path}"
                logger.error(error_message)
                return error_message, 'Failure'

            # Crear el contenido del inventario
            inventory_content = (
                f"{host.ansible_host} "
                f"ansible_user={host.ansible_user} "
                f"ansible_ssh_private_key_file={ssh_key_path} "
                f"ansible_python_interpreter={host.python_interpreter}\n"
            )

            # Crear archivo temporal de inventario
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_inventory:
                temp_inventory.write(inventory_content)
                inventory_path = temp_inventory.name

            # Agregar logs para depuración
            logger.debug(f"Archivo de inventario temporal creado en: {inventory_path}")
            logger.debug(f"Contenido del inventario:\n{inventory_content}")
            logger.debug(f"Ruta del playbook: {playbook_path}")
            logger.debug(f"Host objetivo: {host.ansible_host}")

            # Construir el comando de Ansible
            ansible_command = [
                'ansible-playbook',
                '-i', inventory_path,
                playbook_path,
                '--limit', host.ansible_host,
                '-e', f'host={host.ansible_host}'
            ]

            # Registrar el comando para depuración
            logger.debug(f"Ejecutando comando: {' '.join(ansible_command)}")

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
                # Ejecución fallida
                logger.error(f"Ejecución del playbook fallida con código de retorno {result.returncode}")
                logger.error(f"Salida de error: {result.stderr}")
                return result.stderr, 'Failure'
            else:
                # Ejecución exitosa
                return result.stdout, 'Success'

        except Exception as e:
            logger.exception("Ocurrió un error inesperado durante la ejecución del playbook.")
            return str(e), 'Failure'
        finally:
            # Eliminar el archivo de inventario temporal
            if inventory_path and os.path.exists(inventory_path):
                os.remove(inventory_path)

    def execute_playbook_on_hosts(self, playbook, hosts):
        inventory_path = None
        try:
            # Verificar que los archivos de clave SSH existen
            for host in hosts:
                if not host.ssh_key:
                    error_message = f"El host {host.hostname} no tiene una clave SSH asignada."
                    logger.error(error_message)
                    return error_message, 'Failure'
                #ssh_key_path = host.ssh_key
                ssh_key_path = host.get_ssh_key_path()
                if not os.path.exists(ssh_key_path):
                    error_message = f"La clave SSH no se encuentra en {ssh_key_path} para el host {host.hostname}"
                    logger.error(error_message)
                    return error_message, 'Failure'

            # Verificar que el playbook existe
            playbook_path = playbook.playbook_file.path
            if not os.path.exists(playbook_path):
                error_message = f"El playbook no se encuentra en {playbook_path}"
                logger.error(error_message)
                return error_message, 'Failure'

            # Crear contenido del inventario
            inventory_content = ''
            for host in hosts:
                #ssh_key_path = host.ssh_key
                ssh_key_path = host.get_ssh_key_path()
                inventory_content += (
                    f"{host.ansible_host} "
                    f"ansible_user={host.ansible_user} "
                    f"ansible_ssh_private_key_file={ssh_key_path} "
                    f"ansible_python_interpreter={host.python_interpreter}\n"
                )

            # Crear archivo temporal de inventario
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_inventory:
                temp_inventory.write(inventory_content)
                inventory_path = temp_inventory.name

            # Agregar logs para depuración
            logger.debug(f"Archivo de inventario temporal creado en: {inventory_path}")
            logger.debug(f"Contenido del inventario:\n{inventory_content}")
            logger.debug(f"Ruta del playbook: {playbook_path}")

            # Construir el comando de Ansible
            ansible_command = [
                'ansible-playbook',
                '-i', inventory_path,
                playbook_path,
            ]

            # Registrar el comando para depuración
            logger.debug(f"Ejecutando comando: {' '.join(ansible_command)}")

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
                # Ejecución fallida
                logger.error(f"Ejecución del playbook fallida con código de retorno {result.returncode}")
                logger.error(f"Salida de error: {result.stderr}")
                return result.stderr, 'Failure'
            else:
                # Ejecución exitosa
                return result.stdout, 'Success'

        except Exception as e:
            logger.exception("Ocurrió un error inesperado durante la ejecución del playbook.")
            return str(e), 'Failure'
        finally:
            # Eliminar el archivo de inventario temporal
            if inventory_path and os.path.exists(inventory_path):
                os.remove(inventory_path)

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
            environment = form.cleaned_data['environment']
            group = form.cleaned_data['group']
            host = form.cleaned_data['host']
            playbook = form.cleaned_data['playbook']

            # Agregar logs para depuración
            logger.debug(f"Usuario {request.user.username} está ejecutando el playbook '{playbook.name}' en el host '{host.hostname}'")

            # Ejecutar el playbook en el host
            output, status = self.execute_playbook_on_host(playbook, host)

            # Guardar en el historial
            execution = ExecutionHistory.objects.create(
                playbook=playbook,
                environment=environment,
                group=group,
                host=host,
                executed_by=request.user,
                output=output,
                status=status
            )

            # Mostrar mensaje al usuario
            if status == 'Success':
                messages.success(request, f'Playbook ejecutado exitosamente en {host.hostname}.')
            else:
                messages.error(request, f'Error al ejecutar el playbook en {host.hostname}: {output}')

            return redirect('executor:execution_detail', pk=execution.pk)
        else:
            # Registrar errores del formulario
            logger.error(f"Errores del formulario: {form.errors}")
        return render(request, 'executor/playbook_execute.html', {'form': form})

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
            environment = form.cleaned_data['environment']
            group = form.cleaned_data['group']
            playbook = form.cleaned_data['playbook']

            # Obtener los hosts del grupo
            hosts = group.host_set.all()
            if not hosts:
                logger.error("No se encontraron hosts en el grupo.")
                output, status = "No se encontraron hosts en el grupo.", 'Failure'
            else:
                # Ejecutar el playbook en los hosts
                output, status = self.execute_playbook_on_hosts(playbook, hosts)

            # Guardar en el historial
            execution = ExecutionHistory.objects.create(
                playbook=playbook,
                environment=environment,
                group=group,
                executed_by=request.user,
                output=output,
                status=status
            )

            # Mostrar mensaje al usuario
            if status == 'Success':
                messages.success(request, f'Playbook ejecutado exitosamente en el grupo {group.name}.')
            else:
                messages.error(request, f'Error al ejecutar el playbook en el grupo {group.name}: {output}')

            return redirect('executor:execution_detail', pk=execution.pk)
        else:
            # Registrar errores del formulario
            logger.error(f"Errores del formulario: {form.errors}")
        return render(request, 'executor/playbook_execute_group.html', {'form': form})

class LoadGroupsView(View):
    """
    Vista para cargar grupos basados en el ambiente seleccionado.
    """
    def get(self, request):
        environment_id = request.GET.get('environment_id')
        groups = Group.objects.filter(environment_id=environment_id)
        data = [{'id': group.id, 'name': group.name} for group in groups]
        return JsonResponse({'groups': data})

class LoadHostsView(View):
    """
    Vista para cargar hosts basados en el grupo seleccionado.
    """
    def get(self, request):
        group_id = request.GET.get('group_id')
        hosts = Host.objects.filter(group_id=group_id)
        data = [
            {
                'id': host.id,
                'name': host.hostname,
                'operating_system': host.operating_system
            } for host in hosts
        ]
        return JsonResponse({'hosts': data})

class LoadPlaybooksView(View):
    """
    Vista para cargar playbooks basados en el tipo y sistema operativo.
    """
    def get(self, request):
        playbook_type = request.GET.get('playbook_type')
        if playbook_type == 'host':
            operating_system = request.GET.get('operating_system')
            playbooks = Playbook.objects.filter(
                playbook_type='host',
                operating_system__iexact=operating_system
            )
        elif playbook_type == 'group':
            group_id = request.GET.get('group_id')
            group = get_object_or_404(Group, pk=group_id)
            operating_systems = group.host_set.values_list('operating_system', flat=True).distinct()
            playbooks = Playbook.objects.filter(
                playbook_type='group',
                operating_system__in=operating_systems
            )
        else:
            playbooks = Playbook.objects.none()

        data = [{'id': pb.id, 'name': pb.name} for pb in playbooks]
        return JsonResponse({'playbooks': data})

@login_required
def execution_history(request):
    """
    Vista para mostrar el historial de ejecuciones.
    """
    history = ExecutionHistory.objects.all().order_by('-date')
    return render(request, 'executor/execution_history.html', {'history': history})

@login_required
def execution_detail(request, pk):
    """
    Vista para mostrar los detalles de una ejecución específica.
    """
    execution = get_object_or_404(ExecutionHistory, pk=pk)
    return render(request, 'executor/execution_detail.html', {'execution': execution})
