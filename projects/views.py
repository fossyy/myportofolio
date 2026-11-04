from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods, require_POST

from main.context import PORTFOLIO_PROFILE, model_form_context, section_context
from main.permissions import editor_required, owner_required
from projects.forms import ProjectForm
from projects.models import Project


@ensure_csrf_cookie
def show_projects(request):
    return render(request, "projects.html", section_context(
        request, form=ProjectForm()
    ))


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
