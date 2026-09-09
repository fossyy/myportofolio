import uuid
from datetime import date

from django.db import models


class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ("internship", "Internship"),
        ("research", "Research"),
        ("volunteer", "Volunteer"),
        ("part-time", "Part-Time"),
        ("full-time", "Full-Time"),
        ("freelance", "Freelance"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    organization = models.CharField(max_length=255, default="")
    description = models.TextField()
    project = models.CharField(max_length=255, blank=True)
    technologies = models.CharField(max_length=255, blank=True)
    category = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        default="full-time",
    )
    thumbnail = models.URLField(blank=True, null=True)
    started_at = models.DateField(default=date.today)
    ended_at = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.title

    @property
    def is_ongoing(self):
        return self.ended_at is None

    @property
    def period(self):
        start = self.started_at.strftime("%b %Y")
        end = self.ended_at.strftime("%b %Y") if self.ended_at else "Present"
        return f"{start} — {end}"

    @property
    def tags(self):
        return [tag.strip() for tag in self.technologies.split(",") if tag.strip()]
