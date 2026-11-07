from django.urls import path

from main import api_views

app_name = "api"

urlpatterns = [
    path("experiences/", api_views.experience_list, name="experience_list"),
    path(
        "experiences/<uuid:pk>/",
        api_views.experience_detail,
        name="experience_detail",
    ),
    path(
        "experiences/<uuid:pk>/star/",
        api_views.experience_star,
        name="experience_star",
    ),
    path("skills/", api_views.skill_list, name="skill_list"),
    path("skills/<int:pk>/", api_views.skill_detail, name="skill_detail"),
    path("skills/<int:pk>/star/", api_views.skill_star, name="skill_star"),
]
