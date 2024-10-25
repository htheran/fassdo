# /opt/site/horeb/executor/management/commands/check_scheduled_executions.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from executor.models import ScheduledExecutionHistory
from executor.views import BasePlaybookExecuteView  # Importar la clase base que ejecuta playbooks
from inventory.models import Host

class Command(BaseCommand, BasePlaybookExecuteView):
    help = 'Verifica y ejecuta tareas programadas.'

    def handle(self, *args, **kwargs):
        # Obtener la hora actual
        current_time = timezone.now()

        # Consultar las tareas programadas que están pendientes y cuya hora es igual o anterior a la hora actual
        scheduled_executions = ScheduledExecutionHistory.objects.filter(
            scheduled_date__lte=current_time,
            status='Pending'
        )

        for execution in scheduled_executions:
            try:
                # Determinar si es un host o un grupo
                if execution.host:
                    # Caso de ejecución en un solo host
                    hosts = [execution.host]
                    target_name = execution.host.ansible_host
                    target_type = 'host'
                elif execution.group:
                    # Caso de ejecución en un grupo de hosts
                    hosts = execution.group.host_set.all()  # Obtener todos los hosts del grupo
                    target_name = execution.group.name
                    target_type = 'group'

                # Ejecutar el playbook usando la función ya implementada en BasePlaybookExecuteView
                output, status = self.execute_playbook(execution.playbook, hosts, target_name=target_name, target_type=target_type)

                # Guardar la salida y el estado de la ejecución
                execution.output = output
                execution.status = 'Executed' if status == 'Success' else 'Failed'
                execution.save()

                # Mensaje de éxito o error
                if status == 'Success':
                    self.stdout.write(f"Playbook {execution.playbook.name} ejecutado exitosamente en {target_name}.")
                else:
                    self.stderr.write(f"Error al ejecutar el playbook {execution.playbook.name} en {target_name}: {output}")

            except Exception as e:
                execution.output = f"Error: {str(e)}"
                execution.status = 'Failed'
                execution.save()
                self.stderr.write(f"Error al ejecutar la tarea {execution.id}: {str(e)}")

