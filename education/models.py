from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Education(models.Model):
    qualification = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    start_year = models.PositiveIntegerField(
        validators=[MinValueValidator(1000), MaxValueValidator(9999)]
    )
    end_year = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1000), MaxValueValidator(9999)],
    )

    class Meta:
        ordering = ["-start_year", "pk"]
        verbose_name_plural = "education"
        db_table = "main_education"

    def __str__(self):
        return self.qualification

    def clean(self):
        super().clean()
        if self.start_year is not None and self.end_year is not None and self.end_year < self.start_year:
            raise ValidationError({"end_year": "End year cannot precede start year."})

    @property
    def period(self):
        end = self.end_year if self.end_year is not None else "Present"
        return f"{self.start_year} — {end}"
