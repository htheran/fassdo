# Generated by Django 5.1.2 on 2024-10-19 04:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('executor', '0005_remove_host_group_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='executionhistory',
            options={'verbose_name': 'Execution History', 'verbose_name_plural': 'Execution Histories'},
        ),
    ]