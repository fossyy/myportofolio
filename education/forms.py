from django.forms import ModelForm, NumberInput, TextInput

from education.models import Education


class EducationForm(ModelForm):
    class Meta:
        model = Education
        fields = ["qualification", "institution", "start_year", "end_year"]
        labels = {
            "qualification": "Qualification",
            "institution": "Institution",
            "start_year": "Start Year",
            "end_year": "End Year",
        }
        widgets = {
            "qualification": TextInput(attrs={"placeholder": "Bachelor of Information Systems", "maxlength": 255}),
            "institution": TextInput(attrs={"placeholder": "University of Indonesia", "maxlength": 255}),
            "start_year": NumberInput(attrs={"min": 1000, "max": 9999, "placeholder": "2021"}),
            "end_year": NumberInput(attrs={"min": 1000, "max": 9999, "placeholder": "2025"}),
        }
