from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core.apps.themes.models import ThemeConfiguration
from core.apps.themes.serializers import ThemeConfigurationSerializer


class ThemeConfigurationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing theme configurations.
    Only tenant admins can update their theme.
    """

    queryset = ThemeConfiguration.objects.all()
    serializer_class = ThemeConfigurationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter themes by current tenant"""
        user = self.request.user
        tenant = getattr(self.request, "tenant", None)

        # If no tenant from middleware, try to get from user
        if not tenant and hasattr(user, "tenant"):
            tenant = user.tenant

        if tenant:
            return ThemeConfiguration.objects.filter(tenant=tenant)
        else:
            return ThemeConfiguration.objects.none()

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def current(self, request):
        """Get current tenant's theme configuration"""
        try:
            # Try to get tenant from middleware first
            tenant = getattr(request, "tenant", None)

            # If no tenant from middleware, try to get from user
            if not tenant and hasattr(request.user, "tenant"):
                tenant = request.user.tenant

            # If still no tenant, check if user is superuser
            if not tenant:
                if request.user.is_superuser or getattr(
                    request.user, "is_super", False
                ):
                    # For superusers, return a default theme or first available
                    try:
                        theme = ThemeConfiguration.objects.first()
                        if not theme:
                            # Create a default theme for superuser
                            from core.apps.tenants.models import Tenant

                            default_tenant = Tenant.objects.first()
                            if default_tenant:
                                theme = ThemeConfiguration.objects.create(
                                    tenant=default_tenant
                                )
                    except Exception as e:
                        return Response(
                            {"detail": f"Error fetching theme: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        )
                else:
                    return Response(
                        {"detail": "No tenant associated with this user"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            if not tenant:
                return Response(
                    {"detail": "No tenant found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                theme = ThemeConfiguration.objects.get(tenant=tenant)
            except ThemeConfiguration.DoesNotExist:
                # Create default theme if it doesn't exist
                theme = ThemeConfiguration.objects.create(tenant=tenant)

            serializer = self.get_serializer(theme)
            return Response(serializer.data)
        except Exception as e:
            import traceback

            traceback.print_exc()
            return Response(
                {"detail": f"Error fetching theme: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
        """Update theme - only admins can update"""
        # Check if user is admin
        if request.user.role != "admin" and not request.user.is_super:
            return Response(
                {"detail": "Only admins can update theme configuration"},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Partial update theme - only admins can update"""
        # Check if user is admin
        if request.user.role != "admin" and not request.user.is_super:
            return Response(
                {"detail": "Only admins can update theme configuration"},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        """Ensure tenant is set correctly"""
        try:
            tenant = getattr(self.request, "tenant", None)
            if not tenant and hasattr(self.request.user, "tenant"):
                tenant = self.request.user.tenant

            if not tenant:
                raise ValueError("No tenant associated with user")

            serializer.save(tenant=tenant)
        except Exception:
            import traceback

            traceback.print_exc()
            raise
