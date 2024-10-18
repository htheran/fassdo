
# Create your models here.
from django.db import models

class Playbook(models.Model):
    PLAYBOOK_TYPE_CHOICES = [
        ('group', 'Group'),
        ('host', 'Host'),
    ]

    OS_CHOICES = [
        ('redhat', 'RedHat'),
        ('debian', 'Debian'),
        ('windows', 'Windows'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    playbook_file = models.FileField(upload_to='playbooks/')
    playbook_type = models.CharField(max_length=10, choices=PLAYBOOK_TYPE_CHOICES)
    operating_system = models.CharField(max_length=10, choices=OS_CHOICES)
