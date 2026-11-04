from django.urls import path

from projects import api_views, views

app_name = "projects"

urlpatterns = [
    path("projects/", views.show_projects, name="list"),
    path("projects/add/", views.create_project, name="create"),
    path("projects/<int:project_id>/edit/", views.update_project, name="update"),
    path("projects/<int:project_id>/delete/", views.delete_project, name="delete"),
    path("projects/<int:project_id>/star/", views.toggle_star, name="toggle_star"),
    path("api/v1/projects/", api_views.project_list, name="api_list"),
    path("api/v1/projects/<int:pk>/", api_views.project_detail, name="api_detail"),
    path("api/v1/projects/<int:pk>/star/", api_views.project_star, name="api_star"),
]
