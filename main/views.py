from django.shortcuts import render

from main.models import Experience, Project, Skill

PORTFOLIO_PROFILE = {
    "name": "Bagas Aulia Rezki",
    "short_name": "bagas",
    "npm": "2506656545",
    "role": "fullstack developer",
    "study_program": "information systems student",
    "intro": (
        "I’m a Fullstack Developer and Information Systems student at the "
        "University of Indonesia with experience in backend development, "
        "infrastructure, automation, and self-hosted systems. I enjoy "
        "building efficient, secure, and reliable solutions while continuously "
        "learning new technologies."
    ),
}

def show_main(request):
    context = {
        "profile": PORTFOLIO_PROFILE,
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "profile": PORTFOLIO_PROFILE,
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)


def show_projects(request):
    context = {
        "profile": PORTFOLIO_PROFILE,
        "project_list": Project.objects.all(),
    }
    return render(request, "projects.html", context)


def show_skills(request):
    return render(request, "skills.html", {
        "profile": PORTFOLIO_PROFILE,
        "skill_list": Skill.objects.all(),
    })
