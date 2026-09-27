from django.forms import ModelForm, NumberInput, TextInput

from skills.models import Skill


class SkillForm(ModelForm):
    class Meta:
        model = Skill
        fields = ["name", "category", "position"]
        labels = {"name": "Skill", "category": "Category", "position": "Display Position"}
        widgets = {
            "name": TextInput(attrs={"placeholder": "Django", "maxlength": 100}),
            "category": TextInput(attrs={"placeholder": "Backend", "maxlength": 100}),
            "position": NumberInput(attrs={"min": 0, "placeholder": "0"}),
        }
