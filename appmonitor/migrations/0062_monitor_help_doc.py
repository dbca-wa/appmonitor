# Generated by Django 5.0.8 on 2025-01-29 03:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appmonitor', '0061_pythonpackagevulnerabilityversionadvisoryinformation_basescore_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='monitor',
            name='help_doc',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
    ]
