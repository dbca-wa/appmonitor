# Generated by Django 3.2.19 on 2023-06-28 14:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appmonitor', '0006_manualchecks'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ManualChecks',
            new_name='ManualCheck',
        ),
    ]
