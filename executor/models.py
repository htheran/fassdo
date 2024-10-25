# executor/models.py

from django.db import models
from django.contrib.auth.models import User
from playbook.models import Playbook
from inventory.models import Environment, Group, Host

class ExecutionHistory(models.Model):
    STATUS_CHOICES = [
        ('Success', 'Success'),
        ('Failure', 'Failure'),
    ]

    playbook = models.ForeignKey(Playbook, on_delete=models.CASCADE)
    environment = models.ForeignKey(Environment, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    host = models.ForeignKey(Host, on_delete=models.CASCADE, null=True, blank=True)
    executed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    output = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        verbose_name = "Execution History"
        verbose_name_plural = "Execution Histories"

    def __str__(self):
        return f'{self.playbook.name} executed by {self.executed_by.username} on {self.date}'

############################################################

# Modelo para guardar las ejecuciones programadas
class ScheduledExecutionHistory(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Executed', 'Executed'),
        ('Failed', 'Failed'),
    ]

    playbook = models.ForeignKey(Playbook, on_delete=models.CASCADE)
    environment = models.ForeignKey(Environment, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    host = models.ForeignKey(Host, on_delete=models.CASCADE, null=True, blank=True)
    scheduled_date = models.DateTimeField()
    executed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    output = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Scheduled Execution History"
        verbose_name_plural = "Scheduled Execution Histories"
