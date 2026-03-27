from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.apps.themes.views import ThemeConfigurationViewSet

router = DefaultRouter()
router.register(r"themes", ThemeConfigurationViewSet, basename="theme")

urlpatterns = [
    path("", include(router.urls)),
]
