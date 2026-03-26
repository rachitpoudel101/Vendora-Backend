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

    @action(detail=False, methods=["get"])
    def current(self, request):
        """Get current tenant from request"""
        if request.tenant:
            serializer = self.get_serializer(request.tenant)
            return Response(serializer.data)
        return Response({"detail": "No tenant found"}, status=status.HTTP_404_NOT_FOUND)
