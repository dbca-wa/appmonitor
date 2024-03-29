# Generated by Django 3.2.19 on 2024-01-06 04:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appmonitor', '0021_auto_20240106_0955'),
    ]

    operations = [
        migrations.CreateModel(
            name='Platform',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('system_name', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('api_key', models.CharField(blank=True, default='', help_text='Key is auto generated,  Leave blank or blank out to create a new key', max_length=512, null=True)),
                ('operating_system_name', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('operating_system_version', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('python_version', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('django_version', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('group_responsible', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='appmonitor.responsiblegroup')),
            ],
        ),
    ]
