from datetime import date

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="experience",
            name="organization",
            field=models.CharField(default="", max_length=255),
        ),
        migrations.AddField(
            model_name="experience",
            name="project",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="experience",
            name="technologies",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="experience",
            name="started_at",
            field=models.DateField(default=date.today),
        ),
        migrations.AlterField(
            model_name="experience",
            name="ended_at",
            field=models.DateField(blank=True, null=True),
        ),
    ]
