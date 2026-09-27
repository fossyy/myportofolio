"""Backward-compatible imports for forms now owned by section apps."""

from education.forms import EducationForm
from experiences.forms import ExperienceForm
from projects.forms import ProjectForm
from skills.forms import SkillForm

__all__ = ["EducationForm", "ExperienceForm", "ProjectForm", "SkillForm"]
