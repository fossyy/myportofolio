from django.urls import path

from projects import views

app_name = "projects"

urlpatterns = [
    path("projects/", views.show_projects, name="list"),
    path("projects/add/", views.create_project, name="create"),
    path("projects/add-ajax/", views.create_project_ajax, name="create_ajax"),
    path("projects/<int:project_id>/edit/", views.update_project, name="update"),
    path("projects/<int:project_id>/delete/", views.delete_project, name="delete"),
    path("projects/<int:project_id>/star/", views.toggle_star, name="toggle_star"),
    path("api/projects", views.project_api, name="api_list"),
    path("api/projects/<str:title>", views.project_api, name="api_detail"),
]
