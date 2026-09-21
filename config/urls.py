from django.contrib import admin
from django.urls import path
from library.views import get_authors

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/authors/', get_authors),
]