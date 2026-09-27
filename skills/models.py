from django.db import models


class Skill(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["category", "position", "pk"]
        db_table = "main_skill"

    def __str__(self):
        return self.name
