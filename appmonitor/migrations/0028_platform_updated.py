# Generated by Django 3.2.19 on 2024-01-06 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appmonitor', '0027_auto_20240106_1331'),
    ]

    operations = [
        migrations.AddField(
            model_name='platform',
            name='updated',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
