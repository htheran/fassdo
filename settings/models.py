from django.db import models
import os

def upload_ssh_key_path(instance, filename):
    return os.path.join('ssh_keys/proxmox/', filename)

class Setting(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Variable")
    value = models.TextField(blank=True, null=True, verbose_name="Valor")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")

    def __str__(self):
        return f"{self.name}"

class SSHKey(models.Model):
    private_key = models.FileField(upload_to=upload_ssh_key_path, blank=True, null=True, verbose_name="Llave privada")
    public_key = models.FileField(upload_to=upload_ssh_key_path, blank=True, null=True, verbose_name="Llave pública")

    def __str__(self):
        return "Llaves SSH"
