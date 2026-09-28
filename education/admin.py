from django.contrib import admin

from education.models import Education


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("qualification", "institution", "start_year", "end_year")
    search_fields = ("qualification", "institution")
