import base64
import binascii
import hmac
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from main.forms import EducationForm, ExperienceForm, ProjectForm, SkillForm
from main.models import Education, Experience, Project, Skill

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


def basic_auth_required(view):
    @wraps(view)
    def wrapped_view(request, *args, **kwargs):
        authorization = request.headers.get("Authorization", "")
        credentials = authorization.removeprefix("Basic ")

        try:
            decoded_credentials = base64.b64decode(credentials, validate=True).decode("utf-8")
            username, password = decoded_credentials.split(":", 1)
        except (ValueError, UnicodeDecodeError, binascii.Error):
            username = password = ""

        valid_credentials = (
            hmac.compare_digest(username, settings.BASIC_AUTH_USERNAME)
            and hmac.compare_digest(password, settings.BASIC_AUTH_PASSWORD)
            and bool(settings.BASIC_AUTH_USERNAME)
            and bool(settings.BASIC_AUTH_PASSWORD)
        )
        if not valid_credentials:
            response = HttpResponse("Authentication required.", status=401)
            response["WWW-Authenticate"] = 'Basic realm="Project management"'
            return response

        return view(request, *args, **kwargs)

    return wrapped_view

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


@basic_auth_required
def create_experience(request):
    form = ExperienceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience baru berhasil ditambahkan!")
        return redirect("main:show_experience")

    context = {
        "name": PORTFOLIO_PROFILE["name"],
        "form": form,
    }
    return render(request, "experience_form.html", context)


@basic_auth_required
def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience berhasil dihapus!")

    return redirect("main:show_experience")


def show_projects(request):
    context = {
        "profile": PORTFOLIO_PROFILE,
        "project_list": Project.objects.all(),
    }
    return render(request, "projects.html", context)


def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize("json", projects)
    return HttpResponse(projects_json, content_type="application/json")


@require_http_methods(["GET", "DELETE"])
def project_api(request, title=None):
    if title is None:
        return get_projects_json(request)

    project = get_object_or_404(Project, title=title)
    if request.method == "DELETE":
        return delete_project_api(request, project)

    project_json = serializers.serialize("json", [project])
    return HttpResponse(project_json, content_type="application/json")


@require_http_methods(["GET"])
def experience_api(request):
    experiences_json = serializers.serialize("json", Experience.objects.all())
    return HttpResponse(experiences_json, content_type="application/json")


@require_http_methods(["GET"])
def skill_api(request):
    skills_json = serializers.serialize("json", Skill.objects.all())
    return HttpResponse(skills_json, content_type="application/json")


@require_http_methods(["GET"])
def education_api(request):
    education_json = serializers.serialize("json", Education.objects.all())
    return HttpResponse(education_json, content_type="application/json")


@basic_auth_required
def delete_project_api(request, project):
    project.delete()
    return JsonResponse({"detail": "Project deleted successfully."})


@basic_auth_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Proyek berhasil dihapus!")

    return redirect("main:show_projects")


def show_skills(request):
    return render(request, "skills.html", {
        "profile": PORTFOLIO_PROFILE,
        "skill_list": Skill.objects.all(),
    })


@basic_auth_required
def create_skill(request):
    form = SkillForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Skill baru berhasil ditambahkan!")
        return redirect("main:show_skills")

    return render(request, "skills_form.html", {
        "name": PORTFOLIO_PROFILE["name"],
        "form": form,
    })


@basic_auth_required
def delete_skill(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)

    if request.method == "POST":
        skill.delete()
        messages.success(request, "Skill berhasil dihapus!")

    return redirect("main:show_skills")


def show_education(request):
    return render(request, "education.html", {
        "profile": PORTFOLIO_PROFILE,
        "education_list": Education.objects.all(),
    })


@basic_auth_required
def create_education(request):
    form = EducationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Education baru berhasil ditambahkan!")
        return redirect("main:show_education")

    return render(request, "education_form.html", {
        "name": PORTFOLIO_PROFILE["name"],
        "form": form,
    })


@basic_auth_required
def delete_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)

    if request.method == "POST":
        education.delete()
        messages.success(request, "Education berhasil dihapus!")

    return redirect("main:show_education")

@basic_auth_required
def create_project(request):
    form = ProjectForm(request.POST or None)
    
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_projects")

    context = {
        "name": "Burhan",
        "form": form,
    }
    return render(request, "projects_form.html", context)
