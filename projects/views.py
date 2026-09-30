from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods, require_POST

from main.context import PORTFOLIO_PROFILE, model_form_context, section_context
from main.api import serialize_section
from main.permissions import editor_required, owner_required
from projects.forms import ProjectForm
from projects.models import Project


@ensure_csrf_cookie
def show_projects(request):
    return render(request, "projects.html", section_context(
        request, form=ProjectForm()
    ))


def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.prefetch_related("starred_by").all()
    if title_query:
        projects = projects.filter(title__icontains=title_query)

    data = []
    for project in projects:
        starred_users = list(project.starred_by.all())
        data.append({
            "pk": str(project.pk),
            "model": "main.project",
            "fields": {
                "title": project.title,
                "description": project.description,
                "source_url": project.source_url,
                "live_url": project.live_url,
                "star_count": len(starred_users),
                "is_starred": request.user.is_authenticated and any(
                    user.pk == request.user.pk for user in starred_users
                ),
                "starred_by_names": ", ".join(user.username for user in starred_users),
            },
        })
    return JsonResponse(data, safe=False)


@require_POST
def create_project_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Only the portfolio owner can add projects."}, status=403
        )

    form = ProjectForm(request.POST)
    if form.is_valid():
        project = form.save()
        return JsonResponse(
            {"message": "Project added successfully.", "pk": str(project.pk)},
            status=201,
        )
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


@require_http_methods(["GET", "DELETE"])
def project_api(request, title=None):
    if title is None:
        if request.method != "GET":
            return HttpResponseNotAllowed(["GET"])
        return get_projects_json(request)

    project = get_object_or_404(Project, title=title)
    if request.method == "DELETE":
        return delete_project_api(request, project)
    payload = serialize_section(
        [project], "project", fields=["title", "description", "source_url", "live_url"]
    )
    return HttpResponse(payload, content_type="application/json")


@owner_required
def delete_project_api(request, project):
    project.delete()
    return JsonResponse({"detail": "Project deleted successfully."})


@owner_required
@require_http_methods(["GET", "POST"])
def create_project(request):
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("projects:list")
    context = model_form_context(form, "Project", reverse("projects:create"))
    context["profile"] = PORTFOLIO_PROFILE
    return render(request, "projects_form.html", context)


@editor_required
@require_http_methods(["GET", "POST"])
def update_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek berhasil diperbarui!")
        return redirect("projects:list")
    context = model_form_context(
        form, "Project", reverse("projects:update", args=[project.pk]), is_edit=True
    )
    context["profile"] = PORTFOLIO_PROFILE
    return render(request, "projects_form.html", context)


@owner_required
@require_POST
def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    project.delete()
    messages.success(request, "Proyek berhasil dihapus!")
    return redirect("projects:list")


@login_required(login_url="/login/")
@require_POST
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.starred_by.filter(pk=request.user.pk).exists():
        project.starred_by.remove(request.user)
    else:
        project.starred_by.add(request.user)
    return redirect("projects:list")
