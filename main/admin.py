from django.contrib import admin

from main.models import Experience, Project, Skill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "position")
    list_filter = ("category",)
    search_fields = ("name", "category")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "source_url", "live_url")


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "category", "started_at", "ended_at")
    list_filter = ("category",)
