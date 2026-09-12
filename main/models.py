import uuid
from datetime import date

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


class Skill(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["category", "position", "pk"]

    def __str__(self):
        return self.name


class Education(models.Model):
    qualification = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    start_year = models.PositiveIntegerField(validators=[MinValueValidator(1000), MaxValueValidator(9999)])
    end_year = models.PositiveIntegerField(blank=True, null=True, validators=[MinValueValidator(1000), MaxValueValidator(9999)])

    class Meta:
        ordering = ["-start_year", "pk"]
        verbose_name_plural = "education"

    def __str__(self):
        return self.qualification

    def clean(self):
        super().clean()
        if self.start_year is not None and self.end_year is not None and self.end_year < self.start_year:
            raise ValidationError({"end_year": "End year cannot precede start year."})

    @property
    def period(self):
        return f"{self.start_year} — {self.end_year if self.end_year is not None else 'Present'}"


class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    source_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.title


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
