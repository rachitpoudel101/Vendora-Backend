from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.apps.users.views import (
    ChangePasswordAPIView,
    LogoutView,
    RoleConfigView,
    SelfDetails,
    UserRestoreAPIView,
    UserRoleUpdateAPIView,
    UserViewSet,
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")


urlpatterns = [
    path("", include(router.urls)),
    path("self/", SelfDetails.as_view(), name="self"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "role-update/<int:user_id>/",
        UserRoleUpdateAPIView.as_view(),
        name="role-update",
    ),
    path("role-config/", RoleConfigView.as_view(), name="role-config"),
    path("restore/<int:user_id>/", UserRestoreAPIView.as_view(), name="user-restore"),
    path("change-password/", ChangePasswordAPIView.as_view(), name="change-password"),
    path(
        "change-password/<int:user_id>/",
        ChangePasswordAPIView.as_view(),
        name="change-password-user",
    ),
]
