from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("appmonitor", "0078_platform_vulnerability_total_grype"),
    ]

    operations = [
        migrations.AddField(
            model_name="platformdependabotadvisory",
            name="manifest_path",
            field=models.CharField(blank=True, default="", max_length=512, null=True),
        ),
    ]
