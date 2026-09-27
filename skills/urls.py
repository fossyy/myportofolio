from django.urls import path

from skills import views

app_name = "skills"

urlpatterns = [
    path("skills/", views.show_skills, name="list"),
    path("skills/add/", views.create_skill, name="create"),
    path("skills/<int:skill_id>/edit/", views.update_skill, name="update"),
    path("skills/<int:skill_id>/delete/", views.delete_skill, name="delete"),
    path("api/skills", views.skill_api, name="api_list"),
]
