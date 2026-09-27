from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from main.context import model_form_context, section_context
from main.api import serialize_section
from main.permissions import editor_required, owner_required
from skills.forms import SkillForm
from skills.models import Skill


def show_skills(request):
    return render(request, "skills.html", section_context(
        request, skill_list=Skill.objects.all()
    ))


@owner_required
@require_http_methods(["GET", "POST"])
def create_skill(request):
    form = SkillForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Skill baru berhasil ditambahkan!")
        return redirect("skills:list")
    return render(request, "skills_form.html", model_form_context(
        form, "Skill", reverse("skills:create")
    ))


@editor_required
@require_http_methods(["GET", "POST"])
def update_skill(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)
    form = SkillForm(request.POST or None, instance=skill)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Skill berhasil diperbarui!")
        return redirect("skills:list")
    return render(request, "skills_form.html", model_form_context(
        form, "Skill", reverse("skills:update", args=[skill.pk]), is_edit=True
    ))


@owner_required
@require_POST
def delete_skill(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)
    skill.delete()
    messages.success(request, "Skill berhasil dihapus!")
    return redirect("skills:list")


@require_http_methods(["GET"])
def skill_api(request):
    payload = serialize_section(
        Skill.objects.all(), "skill", fields=["name", "category", "position"]
    )
    return HttpResponse(payload, content_type="application/json")
