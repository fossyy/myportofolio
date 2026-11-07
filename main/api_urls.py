from django.urls import path

from main import api_views as experience_api_views

app_name = "api"

urlpatterns = [
    path("experiences/", experience_api_views.experience_list, name="experience_list"),
    path(
        "experiences/<uuid:pk>/",
        experience_api_views.experience_detail,
        name="experience_detail",
    ),
    path(
        "experiences/<uuid:pk>/star/",
        experience_api_views.experience_star,
        name="experience_star",
    ),
]
