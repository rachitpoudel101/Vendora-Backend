from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.apps.inventory.views import (
    CategoryViewSet,
    ProductViewSet,
    UnitTypeConfigurationsViewSet,
    UnitTypeViewSet,
)

router = DefaultRouter()
router.register(r"unit", UnitTypeViewSet, basename="unit")
router.register(r"category", CategoryViewSet, basename="category")
router.register(r"product", ProductViewSet, basename="product")
router.register(
    r"unit-configurations",
    UnitTypeConfigurationsViewSet,
    basename="unit-configurations",
)


urlpatterns = [
    path("", include(router.urls)),
]
