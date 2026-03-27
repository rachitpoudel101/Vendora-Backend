from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Tenant
from .serializers import TenantSerializer


class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    lookup_field = "id"

    def get_permissions(self):
        """Allow superusers to manage all tenants"""
        return [IsAuthenticated()]

    def get_queryset(self):
        """Allow superusers to see all tenants, others see only their own"""
        if self.request.user.is_superuser or self.request.user.is_super:
            return Tenant.objects.all()
        # Regular users see only their tenant
        if hasattr(self.request.user, "tenant") and self.request.user.tenant:
            return Tenant.objects.filter(id=self.request.user.tenant.id)
        return Tenant.objects.none()

    def destroy(self, request, *args, **kwargs):
        """Delete a tenant - only superusers allowed"""
        # Only superusers can delete tenants
        is_super = request.user.is_superuser or getattr(request.user, "is_super", False)
        if not is_super:
            return Response(
                {"error": "Only superadmin can delete tenants"},
                status=status.HTTP_403_FORBIDDEN,
            )

        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        """Create a tenant - only superusers allowed"""
        # Only superusers can create tenants
        is_super = request.user.is_superuser or getattr(request.user, "is_super", False)
        if not is_super:
            return Response(
                {"error": "Only superadmin can create tenants"},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Update a tenant - only superusers or tenant admin can update their own"""
        instance = self.get_object()
        is_super = request.user.is_superuser or getattr(request.user, "is_super", False)

        # Superusers can update any tenant
        if is_super:
            return super().update(request, *args, **kwargs)

        # Tenant admins can only update their own tenant
        if hasattr(request.user, "tenant") and request.user.tenant == instance:
            return super().update(request, *args, **kwargs)

        return Response(
            {"error": "You can only update your own tenant"},
            status=status.HTTP_403_FORBIDDEN,
        )

    @action(detail=False, methods=["get"])
    def current(self, request):
        """Get current tenant from request"""
        if request.tenant:
            serializer = self.get_serializer(request.tenant)
            return Response(serializer.data)
        return Response({"detail": "No tenant found"}, status=status.HTTP_404_NOT_FOUND)
