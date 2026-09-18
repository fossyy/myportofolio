from django.forms import DateInput, ModelForm, Select, TextInput, Textarea, URLInput

from main.models import Experience, Project


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "source_url",
            "live_url",
        ]

        labels = {
            "title": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "source_url": "URL Source Code",
            "live_url": "URL Live Project",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Portfolio Website",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Tell us about your project",
                    "rows": 3,
                }
            ),
            "source_url": URLInput(
                attrs={
                    "placeholder": "https://github.com/username/project",
                }
            ),
            "live_url": URLInput(
                attrs={
                    "placeholder": "https://example.com",
                }
            ),
        }


class ExperienceForm(ModelForm):
    class Meta:
        model = Experience
        fields = [
            "title",
            "organization",
            "description",
            "project",
            "technologies",
            "category",
            "thumbnail",
            "started_at",
            "ended_at",
        ]

        labels = {
            "title": "Role / Title",
            "organization": "Organization",
            "description": "Description",
            "project": "Related Project",
            "technologies": "Technologies",
            "category": "Category",
            "thumbnail": "Thumbnail URL",
            "started_at": "Start Date",
            "ended_at": "End Date",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Backend Developer Intern",
                    "maxlength": 255,
                }
            ),
            "organization": TextInput(
                attrs={
                    "placeholder": "Company or organization",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Tell us about this experience",
                    "rows": 4,
                }
            ),
            "project": TextInput(
                attrs={
                    "placeholder": "Project or contribution",
                    "maxlength": 255,
                }
            ),
            "technologies": TextInput(
                attrs={
                    "placeholder": "Django, Python, PostgreSQL",
                    "maxlength": 255,
                }
            ),
            "category": Select(),
            "thumbnail": URLInput(
                attrs={
                    "placeholder": "https://example.com/thumbnail.jpg",
                }
            ),
            "started_at": DateInput(attrs={"type": "date"}),
            "ended_at": DateInput(attrs={"type": "date"}),
        }
