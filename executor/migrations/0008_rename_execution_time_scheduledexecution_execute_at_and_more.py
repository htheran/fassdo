# Generated by Django 5.1.2 on 2024-10-25 00:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('executor', '0007_scheduledexecution'),
    ]

    operations = [
        migrations.RenameField(
            model_name='scheduledexecution',
            old_name='execution_time',
            new_name='execute_at',
        ),
        migrations.RemoveField(
            model_name='scheduledexecution',
            name='output',
        ),
    ]