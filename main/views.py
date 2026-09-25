import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import PermissionDenied
from django.core import serializers
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

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


def can_edit_content(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name="Editor").exists()
    )


def owner_required(view):
    def check_owner(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return login_required(check_owner, login_url="/login/")


def editor_required(view):
    def check_editor(request, *args, **kwargs):
        if not can_edit_content(request.user):
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return login_required(check_editor, login_url="/login/")


def section_context(request, **context):
    return {
        "profile": PORTFOLIO_PROFILE,
        "can_edit_content": can_edit_content(request.user),
        "is_portfolio_owner": request.user.is_superuser,
        **context,
    }

def show_main(request):
    context = {
        "profile": PORTFOLIO_PROFILE,
        "last_login": request.COOKIES.get("last_login", "No active login session / Cookie not found"),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = section_context(request, experience_list=Experience.objects.all())
    return render(request, "experience.html", context)


@owner_required
@require_http_methods(["GET", "POST"])
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


@owner_required
@require_POST
def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience berhasil dihapus!")

    return redirect("main:show_experience")


def show_projects(request):
    context = section_context(request, project_list=Project.objects.all())
    return render(request, "projects.html", context)


def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize(
        "json", projects, fields=["title", "description", "source_url", "live_url"]
    )
    return HttpResponse(projects_json, content_type="application/json")


@require_http_methods(["GET", "DELETE"])
def project_api(request, title=None):
    if title is None:
        if request.method != "GET":
            return HttpResponseNotAllowed(["GET"])
        return get_projects_json(request)

    project = get_object_or_404(Project, title=title)
    if request.method == "DELETE":
        return delete_project_api(request, project)

    project_json = serializers.serialize(
        "json", [project], fields=["title", "description", "source_url", "live_url"]
    )
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


@owner_required
def delete_project_api(request, project):
    project.delete()
    return JsonResponse({"detail": "Project deleted successfully."})


@owner_required
@require_POST
def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Proyek berhasil dihapus!")

    return redirect("main:show_projects")


def show_skills(request):
    return render(request, "skills.html", section_context(request, skill_list=Skill.objects.all()))


@owner_required
@require_http_methods(["GET", "POST"])
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


@owner_required
@require_POST
def delete_skill(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)

    if request.method == "POST":
        skill.delete()
        messages.success(request, "Skill berhasil dihapus!")

    return redirect("main:show_skills")


def show_education(request):
    return render(request, "education.html", section_context(request, education_list=Education.objects.all()))


@owner_required
@require_http_methods(["GET", "POST"])
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


@owner_required
@require_POST
def delete_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)

    if request.method == "POST":
        education.delete()
        messages.success(request, "Education berhasil dihapus!")

    return redirect("main:show_education")

@owner_required
@require_http_methods(["GET", "POST"])
def create_project(request):
    form = ProjectForm(request.POST or None)
    
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_projects")

    context = {
        "name": PORTFOLIO_PROFILE["name"],
        "form": form,
    }
    return render(request, "projects_form.html", context)


def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Account created successfully. Please log in.")
        return redirect("main:login")
    return render(request, "register.html", {
        "name": PORTFOLIO_PROFILE["name"],
        "profile": PORTFOLIO_PROFILE,
        "form": form,
    })


def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        response = redirect("main:show_main")
        response.set_cookie("last_login", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return response
    return render(request, "login.html", {
        "name": PORTFOLIO_PROFILE["name"],
        "profile": PORTFOLIO_PROFILE,
        "form": form,
    })


def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login")
    return response


@login_required(login_url="/login/")
@require_POST
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        if request.user in project.starred_by.all():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)
    return redirect("main:show_projects")
