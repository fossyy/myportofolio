"""Backward-compatible imports for models now owned by section apps."""

from education.models import Education
from experiences.models import Experience
from projects.models import Project
from skills.models import Skill

__all__ = ["Education", "Experience", "Project", "Skill"]
