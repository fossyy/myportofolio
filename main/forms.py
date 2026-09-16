from django.forms import ModelForm, TextInput, Textarea, URLInput

from main.models import Project


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