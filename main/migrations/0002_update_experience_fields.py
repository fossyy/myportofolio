from datetime import date

from django.db import migrations, models


def seed_experience(apps, schema_editor):
    Experience = apps.get_model("main", "Experience")
    Experience.objects.get_or_create(
        title="Back-end Developer Intern",
        defaults={
            "organization": "PT eBdesk Teknologi",
            "description": (
                "Developed a flexible web-crawling system capable of extracting "
                "data from different website structures without requiring a "
                "completely new crawler for every website."
            ),
            "project": "Dynamic Web Crawling System",
            "technologies": "Go, Tailwind CSS, Templ, HTMX",
            "category": "internship",
            "started_at": date(2024, 10, 1),
            "ended_at": date(2025, 4, 30),
        },
    )


def remove_bagas_experience(apps, schema_editor):
    Experience = apps.get_model("main", "Experience")
    Experience.objects.filter(title="Back-end Developer Intern").delete()


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
        migrations.RunPython(seed_experience, remove_bagas_experience),
    ]
