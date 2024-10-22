# inventory/models.py

from django.db import models
import os
from django.conf import settings

class Environment(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    environment = models.ForeignKey(Environment, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Host(models.Model):
    ENV_CHOICES = [('Redhat', 'Redhat'), ('Debian', 'Debian'), ('Windows', 'Windows')]

    environment = models.ForeignKey(Environment, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    hostname = models.CharField(max_length=100)
    ansible_host = models.CharField(max_length=100)
    ansible_user = models.CharField(max_length=50, default='root')
    operating_system = models.CharField(max_length=50, choices=ENV_CHOICES)
    python_interpreter = models.CharField(max_length=100, default='/usr/bin/python3.12')
    ssh_key = models.CharField(max_length=255, default='media/ssh_keys/id_rsa')

    def __str__(self):
        return self.hostname

    # Obtener la ruta completa de la clave SSH en el servidor
    def get_ssh_key_path(self):
        return os.path.join(settings.BASE_DIR, self.ssh_key)


class SSHConnectionHistory(models.Model):
    environment = models.ForeignKey(Environment, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    host = models.ForeignKey(Host, on_delete=models.CASCADE)
    fingerprint = models.CharField(max_length=255)  # Hash de la clave SSH o detalles únicos del host
    accepted = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.host.hostname} - Aceptado: {self.accepted} - {self.date}'


# service_manager/models.py

class ServiceActionLog(models.Model):
    ACTION_CHOICES = [
        ('start', 'Iniciar'),
        ('stop', 'Detener'),
        ('restart', 'Reiniciar'),
        ('status', 'Ver estado')
    ]
    service_name = models.CharField(max_length=50)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    host = models.ForeignKey(Host, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    output = models.TextField()  # Guardar la salida del comando ejecutado
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.service_name} - {self.action} - {self.status} - {self.timestamp}'
