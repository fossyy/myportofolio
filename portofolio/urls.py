from django.contrib import admin
from django.urls import include, path

from portofolio.views import landing_page

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("main.urls")),
]