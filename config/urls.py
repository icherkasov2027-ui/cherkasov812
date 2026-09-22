from django.contrib import admin
from django.urls import path
from library.views import get_projects

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/projects/', get_projects),
]