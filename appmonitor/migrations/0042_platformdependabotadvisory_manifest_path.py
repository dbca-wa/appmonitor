from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appmonitor', '0041_alter_accessgroup_access_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='platformdependabotadvisory',
            name='manifest_path',
            field=models.CharField(blank=True, default='', max_length=512, null=True),
        ),
    ]
