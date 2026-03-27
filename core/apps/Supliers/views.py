from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.apps.Supliers.models import Supliers
from core.apps.Supliers.serializers import SupliersCreateSerializer, SupliersSerializer
from core.apps.users.permissions.permissions import IsAdmin, IsSuperAdmin


class SupliersListCreateView(generics.ListCreateAPIView):
    queryset = Supliers.objects.filter(is_deleted=False)
    serializer_class = SupliersCreateSerializer
    permission_classes = [IsAdmin | IsSuperAdmin]

    def get_queryset(self):
        """Filter suppliers by current tenant"""
        tenant = getattr(self.request, "tenant", None)

        # If no tenant from middleware, try to get from user
        if not tenant and self.request.user and hasattr(self.request.user, "tenant"):
            tenant = self.request.user.tenant

        if tenant:
            return Supliers.objects.filter(tenant=tenant, is_deleted=False)
        return Supliers.objects.none()

    def perform_create(self, serializer):
        """Set tenant when creating supplier"""
        tenant = getattr(self.request, "tenant", None)
        if not tenant and self.request.user and hasattr(self.request.user, "tenant"):
            tenant = self.request.user.tenant
        serializer.save(tenant=tenant)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SupliersCreateSerializer
        return SupliersSerializer


class SupliersDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdmin | IsSuperAdmin]
    queryset = Supliers.objects.filter(is_deleted=False)
    serializer_class = SupliersCreateSerializer
    lookup_field = "id"

    def get_queryset(self):
        """Filter suppliers by current tenant"""
        tenant = getattr(self.request, "tenant", None)

        # If no tenant from middleware, try to get from user
        if not tenant and self.request.user and hasattr(self.request.user, "tenant"):
            tenant = self.request.user.tenant

        if tenant:
            return Supliers.objects.filter(tenant=tenant, is_deleted=False)
        return Supliers.objects.none()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
