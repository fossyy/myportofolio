from django.urls import path

from experiences import views

app_name = "experiences"

urlpatterns = [
    path("experience/", views.show_experience, name="list"),
    path("experience/add/", views.create_experience, name="create"),
    path("experience/<uuid:experience_id>/edit/", views.update_experience, name="update"),
    path("experience/<uuid:experience_id>/delete/", views.delete_experience, name="delete"),
    path("api/experience", views.experience_api, name="api_list"),
]
