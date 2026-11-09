from django.conf import settings
from django.db import models


class Skill(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    position = models.PositiveIntegerField(default=0)
    starred_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="starred_skills",
        blank=True,
        db_table="main_skill_starred_by",
    )

    class Meta:
        ordering = ["category", "position", "pk"]
        db_table = "main_skill"

    def __str__(self):
        return self.name
