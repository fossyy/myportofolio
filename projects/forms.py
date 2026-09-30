from django.forms import ModelForm, TextInput, Textarea, URLInput
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

from projects.models import Project


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ["title", "description", "source_url", "live_url"]
        labels = {
            "title": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "source_url": "URL Source Code",
            "live_url": "URL Live Project",
        }
        widgets = {
            "title": TextInput(attrs={"placeholder": "Portfolio Website", "maxlength": 255}),
            "description": Textarea(attrs={"placeholder": "Tell us about your project", "rows": 3}),
            "source_url": URLInput(attrs={"placeholder": "https://github.com/username/project"}),
            "live_url": URLInput(attrs={"placeholder": "https://example.com"}),
        }

    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError("Project name can't contain only HTML tags.")
        return title

    def clean_description(self):
        return strip_tags(self.cleaned_data["description"]).strip()
