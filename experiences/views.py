from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from experiences.forms import ExperienceForm
from experiences.models import Experience
from main.context import model_form_context, section_context
from main.permissions import editor_required, owner_required


@ensure_csrf_cookie
def show_experience(request):
    return render(request, "experience.html", section_context(
        request, form=ExperienceForm()
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


@require_GET
def experience_api(request):
    title_query = request.GET.get("title", "").strip()
    experiences = Experience.objects.prefetch_related("starred_by").all()
    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    data = []
    for experience in experiences:
        starred_users = list(experience.starred_by.all())
        data.append({
            "pk": str(experience.pk),
            "model": "experiences.experience",
            "fields": {
                "title": experience.title,
                "organization": experience.organization,
                "description": experience.description,
                "project": experience.project,
                "technologies": experience.technologies,
                "category": experience.category,
                "category_display": experience.get_category_display(),
                "thumbnail": experience.thumbnail or "",
                "started_at": experience.started_at.isoformat(),
                "ended_at": experience.ended_at.isoformat() if experience.ended_at else "",
                "period": experience.period,
                "is_ongoing": experience.is_ongoing,
                "star_count": len(starred_users),
                "is_starred": request.user.is_authenticated and any(
                    user.pk == request.user.pk for user in starred_users
                ),
            },
        })
    return JsonResponse(data, safe=False)


@require_POST
def create_experience_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Only the portfolio owner can add experience."}, status=403
        )

    form = ExperienceForm(request.POST)
    if form.is_valid():
        experience = form.save()
        return JsonResponse(
            {"message": "Experience added successfully.", "pk": str(experience.pk)},
            status=201,
        )
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


@require_POST
def toggle_experience_star(request, experience_id):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "Log in to star this experience."}, status=403)

    experience = get_object_or_404(Experience, pk=experience_id)
    if experience.starred_by.filter(pk=request.user.pk).exists():
        experience.starred_by.remove(request.user)
    else:
        experience.starred_by.add(request.user)
    return JsonResponse({"starred": experience.starred_by.filter(pk=request.user.pk).exists()})
