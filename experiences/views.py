from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from experiences.forms import ExperienceForm
from experiences.models import Experience
from main.context import model_form_context, section_context
from main.api import serialize_section
from main.permissions import editor_required, owner_required


def show_experience(request):
    return render(request, "experience.html", section_context(
        request, experience_list=Experience.objects.all()
    ))


@owner_required
@require_http_methods(["GET", "POST"])
def create_experience(request):
    form = ExperienceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience baru berhasil ditambahkan!")
        return redirect("experiences:list")
    context = model_form_context(form, "Experience", reverse("experiences:create"))
    return render(request, "experience_form.html", context)


@editor_required
@require_http_methods(["GET", "POST"])
def update_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    form = ExperienceForm(request.POST or None, instance=experience)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience berhasil diperbarui!")
        return redirect("experiences:list")
    context = model_form_context(
        form, "Experience", reverse("experiences:update", args=[experience.pk]), is_edit=True
    )
    return render(request, "experience_form.html", context)


@owner_required
@require_POST
def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    experience.delete()
    messages.success(request, "Experience berhasil dihapus!")
    return redirect("experiences:list")


@require_http_methods(["GET"])
def experience_api(request):
    fields = [
        "title", "organization", "description", "project", "technologies",
        "category", "thumbnail", "started_at", "ended_at",
    ]
    payload = serialize_section(Experience.objects.all(), "experience", fields=fields)
    return HttpResponse(payload, content_type="application/json")
