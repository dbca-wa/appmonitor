# Generated by Django 3.2.19 on 2023-06-28 14:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appmonitor', '0005_monitor_use_auth2_token'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManualChecks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_name', models.CharField(max_length=50)),
                ('check_url', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('system_id', models.CharField(blank=True, default='', max_length=50, null=True)),
                ('group_responsible', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='appmonitor.responsiblegroup')),
            ],
        ),
    ]
