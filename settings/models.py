
# Create your models here.
from django.db import models
import os

def upload_ssh_key_path(instance, filename):
    # Guardar las llaves SSH en la carpeta 'media/ssh_keys'
    return os.path.join('ssh_keys', filename)

class Setting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.key

class SSHKey(models.Model):
    private_key = models.FileField(upload_to=upload_ssh_key_path)
    public_key = models.FileField(upload_to=upload_ssh_key_path)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Establecer permisos correctos para las llaves
        os.chmod(self.private_key.path, 0o600)
        os.chmod(self.public_key.path, 0o755)

    def __str__(self):
        return "SSH Keys"
