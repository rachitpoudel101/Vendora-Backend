from rest_framework import permissions


class IsTenantUser(permissions.BasePermission):
    """Check if user belongs to the requested tenant"""

    def has_permission(self, request, view):
        if not request.tenant:
            return False

        if not request.user or not request.user.is_authenticated:
            return False

        # Check if user belongs to this tenant
        return request.user.tenant == request.tenant

    def has_object_permission(self, request, view, obj):
        if not hasattr(obj, "tenant"):
            return True

        return obj.tenant == request.tenant
