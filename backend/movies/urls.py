from django.contrib import admin
from django.urls import path
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter(trailing_slash=False)

router.register('movies', views.MovieViewSet, basename='movies')

urlpatterns = [
    path('admin/', admin.site.urls),
] + router.urls
