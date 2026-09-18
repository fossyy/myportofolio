from django.urls import path

from main.views import (
    create_experience,
    create_project,
    delete_experience,
    delete_project,
    project_api,
    show_education,
    show_experience,
    show_main,
    show_projects,
    show_skills,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("experience/add/", create_experience, name="create_experience"),
    path("experience/<uuid:experience_id>/delete/", delete_experience, name="delete_experience"),
    path("projects/", show_projects, name="show_projects"),
    path("projects/add/", create_project, name="create_project"),
    path("projects/<int:project_id>/delete/", delete_project, name="delete_project"),
    path("api/projects", project_api, name="projects_api"),
    path("api/projects/<str:title>", project_api, name="project_api"),
    path("skills/", show_skills, name="show_skills"),
    path("education/", show_education, name="show_education"),
]
