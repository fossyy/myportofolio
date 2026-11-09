from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods, require_POST

from education.forms import EducationForm
from education.models import Education
from main.context import model_form_context, section_context
from main.permissions import editor_required, owner_required


@ensure_csrf_cookie
def show_education(request):
    return render(request, "education.html", section_context(
        request, form=EducationForm()
    ))


@owner_required
@require_http_methods(["GET", "POST"])
def create_education(request):
    form = EducationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Education baru berhasil ditambahkan!")
        return redirect("education:list")
    return render(request, "education_form.html", model_form_context(
        form, "Education", reverse("education:create")
    ))


@editor_required
@require_http_methods(["GET", "POST"])
def update_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)
    form = EducationForm(request.POST or None, instance=education)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Education berhasil diperbarui!")
        return redirect("education:list")
    return render(request, "education_form.html", model_form_context(
        form, "Education", reverse("education:update", args=[education.pk]), is_edit=True
    ))


@owner_required
@require_POST
def delete_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)
    education.delete()
    messages.success(request, "Education berhasil dihapus!")
    return redirect("education:list")
