# Generated by Django 3.2.19 on 2023-08-28 08:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appmonitor', '0014_auto_20230728_2237'),
    ]

    operations = [
        migrations.CreateModel(
            name='TicketFilter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('url', models.CharField(blank=True, default='', max_length=2000, null=True)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='TicketFilterNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('ticket_filter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='appmonitor.ticketfilter')),
            ],
        ),
    ]
