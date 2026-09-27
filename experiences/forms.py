from django.forms import DateInput, ModelForm, Select, TextInput, Textarea, URLInput

from experiences.models import Experience


class ExperienceForm(ModelForm):
    class Meta:
        model = Experience
        fields = [
            "title", "organization", "description", "project", "technologies",
            "category", "thumbnail", "started_at", "ended_at",
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
            "title": TextInput(attrs={"placeholder": "Backend Developer Intern", "maxlength": 255}),
            "organization": TextInput(attrs={"placeholder": "Company or organization", "maxlength": 255}),
            "description": Textarea(attrs={"placeholder": "Tell us about this experience", "rows": 4}),
            "project": TextInput(attrs={"placeholder": "Project or contribution", "maxlength": 255}),
            "technologies": TextInput(attrs={"placeholder": "Django, Python, PostgreSQL", "maxlength": 255}),
            "category": Select(),
            "thumbnail": URLInput(attrs={"placeholder": "https://example.com/thumbnail.jpg"}),
            "started_at": DateInput(attrs={"type": "date"}),
            "ended_at": DateInput(attrs={"type": "date"}),
        }
