
# Create your views here.
# service_manager/views.py

import paramiko
from django.shortcuts import render, redirect
from .forms import ServiceManagerForm
from django.contrib.auth.decorators import login_required
from inventory.models import Environment, Group, Host
from django.contrib import messages
from .forms import HostStatusForm 
import psutil
import os



@login_required
def manage_services(request):
    output = ""
    services = ['httpd', 'firewalld', 'nginx', 'vsftpd', 'mariadb', 'postgresql', 'NetworkManager']

    if request.method == 'POST':
        form = ServiceManagerForm(request.POST)
        if form.is_valid():
            environment = form.cleaned_data.get('environment')
            group = form.cleaned_data.get('group')
            host = form.cleaned_data.get('host')
            service = form.cleaned_data.get('service_name')
            action = form.cleaned_data.get('action')

            # Obtener detalles del host
            username = host.ansible_user
            private_key_path = host.get_ssh_key_path()
            target_host = host.ansible_host

            # Verificar que la clave privada existe
            if not os.path.exists(private_key_path):
                output = f"La clave privada {private_key_path} no existe."
                messages.error(request, output)
                return render(request, 'service_manager/manage_services.html', {
                    'form': form,
                    'status_output': output
                })

            try:
                # Configurar el cliente SSH
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                key = paramiko.RSAKey.from_private_key_file(private_key_path)

                # Establecer la conexión SSH
                ssh.connect(
                    hostname=target_host,
                    username=username,
                    pkey=key,
                    timeout=10
                )

                # Verificar el estado del servicio
                check_command = f"systemctl is-active {service}"
                stdin, stdout, stderr = ssh.exec_command(check_command)
                status_output = stdout.read().decode('utf-8').strip()
                error_output = stderr.read().decode('utf-8').strip()

                if status_output not in ["active", "inactive", "failed"]:
                    output = f"Error al verificar el estado de {service}: {error_output or 'Servicio no encontrado o error desconocido.'}"
                    messages.error(request, output)
                else:
                    output = f"El estado del servicio {service} es: {status_output}\n"

                    # Ejecutar la acción sobre el servicio
                    action_command = f"sudo systemctl {action} {service}"
                    stdin, stdout, stderr = ssh.exec_command(action_command)
                    action_output = stdout.read().decode('utf-8').strip() or stderr.read().decode('utf-8').strip()
                    exit_status = stdout.channel.recv_exit_status()

                    if exit_status == 0:
                        output += f"Acción '{action}' ejecutada con éxito en {service}."
                        messages.success(request, output)
                    else:
                        output += f"Error al ejecutar la acción '{action}' en {service}: {action_output}"
                        messages.error(request, output)

                ssh.close()

            except paramiko.AuthenticationException:
                output = "Error de autenticación. Verifica las credenciales."
                messages.error(request, output)
            except paramiko.SSHException as sshException:
                output = f"Error de conexión SSH: {sshException}"
                messages.error(request, output)
            except Exception as e:
                output = f"Error al procesar la solicitud: {str(e)}"
                messages.error(request, output)
    else:
        form = ServiceManagerForm()

    return render(request, 'service_manager/manage_services.html', {
        'form': form,
        'services': services,
        'status_output': output
    })



# service_manager/views.py
@login_required
def host_status(request):
    cpu_info = {}
    ram_info = {}
    disk_info = []
    firewall_ports = []

    selected_environment = None
    selected_group = None
    selected_host = None

    if request.method == 'POST':
        form = HostStatusForm(request.POST)
        if form.is_valid():
            selected_environment = form.cleaned_data.get('environment')
            selected_group = form.cleaned_data.get('group')
            selected_host = form.cleaned_data.get('host')

            # Obtener detalles del host
            username = selected_host.ansible_user
            private_key_path = selected_host.get_ssh_key_path()
            target_host = selected_host.ansible_host

            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                key = paramiko.RSAKey.from_private_key_file(private_key_path)
                ssh.connect(hostname=target_host, username=username, pkey=key, timeout=10)

                # Obtener información de CPU
                cpu_command = "top -bn1 | grep 'Cpu(s)'"
                stdin, stdout, stderr = ssh.exec_command(cpu_command)
                cpu_output = stdout.read().decode('utf-8')
                cpu_usage = float(cpu_output.split()[1])
                cpu_info = {'usage': cpu_usage}

                # Obtener información de RAM
                ram_command = "free -m"
                stdin, stdout, stderr = ssh.exec_command(ram_command)
                ram_output = stdout.read().decode('utf-8')
                ram_lines = ram_output.splitlines()
                ram_total = int(ram_lines[1].split()[1])
                ram_used = int(ram_lines[1].split()[2])
                ram_percent = (ram_used / ram_total) * 100
                ram_info = {'total': ram_total, 'used': ram_used, 'percent': ram_percent}

                # Obtener información de Disco
                disk_command = "df -h"
                stdin, stdout, stderr = ssh.exec_command(disk_command)
                disk_output = stdout.read().decode('utf-8')
                disk_lines = disk_output.splitlines()[1:]
                for line in disk_lines:
                    parts = line.split()
                    disk_percent = int(parts[4].strip('%'))
                    disk_info.append({
                        'filesystem': parts[0],
                        'size': parts[1],
                        'used': parts[2],
                        'avail': parts[3],
                        'percent': disk_percent,
                        'mount': parts[5]
                    })

                # Obtener información de Puertos de firewalld
                ports_command = "sudo firewall-cmd --list-ports"
                stdin, stdout, stderr = ssh.exec_command(ports_command)
                ports_output = stdout.read().decode('utf-8')
                firewall_ports = ports_output.split()

                ssh.close()

            except Exception as e:
                messages.error(request, f"Error al conectarse al host: {e}")

    else:
        form = HostStatusForm()

    return render(request, 'service_manager/host_status.html', {
        'form': form,
        'selected_environment': selected_environment,
        'selected_group': selected_group,
        'selected_host': selected_host,
        'cpu_info': cpu_info,
        'ram_info': ram_info,
        'disk_info': disk_info,
        'firewall_ports': firewall_ports,
    })