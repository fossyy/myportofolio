from django.urls import path

from education import views

app_name = "education"

urlpatterns = [
    path("education/", views.show_education, name="list"),
    path("education/add/", views.create_education, name="create"),
    path("education/<int:education_id>/edit/", views.update_education, name="update"),
    path("education/<int:education_id>/delete/", views.delete_education, name="delete"),
    path("api/education", views.education_api, name="api_list"),
]
