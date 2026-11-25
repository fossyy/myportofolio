from django.urls import path
from rest_framework.authtoken import views as authtoken_views

from main import api_views

app_name = "api"

urlpatterns = [
    path("auth/token/", authtoken_views.obtain_auth_token, name="api_token_auth"),
    path("auth/logout/", api_views.api_logout, name="api_logout"),
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
    path("education/", api_views.education_list, name="education_list"),
    path("education/<int:pk>/", api_views.education_detail, name="education_detail"),
    path("education/<int:pk>/star/", api_views.education_star, name="education_star"),
]
