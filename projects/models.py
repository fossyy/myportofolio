from django.conf import settings
from django.db import models


class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    source_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    starred_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="starred_projects",
        blank=True,
        db_table="main_project_starred_by",
    )

    class Meta:
        ordering = ["pk"]
        db_table = "main_project"

    def __str__(self):
        return self.title
