# Generated by Django 5.0.9 on 2024-11-29 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appmonitor', '0057_rename_pythondependabotadvisory_platformdependabotadvisory'),
    ]

    operations = [
        migrations.AddField(
            model_name='platformdependabotadvisory',
            name='number',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='platformdependabotadvisory',
            name='state',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
    ]