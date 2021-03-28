from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter(trailing_slash=False)
router.register('movies', views.MovieViewSet, basename='movies')

urlpatterns = [
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
]
