from django.utils.deprecation import MiddlewareMixin
from .models import Tenant


class TenantMiddleware(MiddlewareMixin):
    """Middleware to set current tenant based on request"""

    def process_request(self, request):
        # Get tenant from subdomain or URL parameter
        tenant_slug = self.get_tenant_slug(request)

        if tenant_slug:
            try:
                tenant = Tenant.objects.get(slug=tenant_slug, is_active=True)
                request.tenant = tenant
            except Tenant.DoesNotExist:
                request.tenant = None
        else:
            request.tenant = None

        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Set tenant from authenticated user if not already set"""
        # If tenant not set from URL/subdomain, try to get from authenticated user
        if not request.tenant and hasattr(request, "user") and request.user:
            if request.user.is_authenticated:
                # Get tenant from authenticated user
                user_tenant = getattr(request.user, "tenant", None)
                if user_tenant:
                    request.tenant = user_tenant
                # For superusers without a tenant, allow access to all data
                elif request.user.is_superuser or getattr(
                    request.user, "is_super", False
                ):
                    request.tenant = (
                        None  # Superusers can access without tenant restriction
                    )
                else:
                    request.tenant = None

        return None

    def get_tenant_slug(self, request):
        """Extract tenant slug from subdomain or URL"""
        # From subdomain: tenant.example.com
        host = request.get_host().split(":")[0]
        parts = host.split(".")

        if len(parts) > 2:
            return parts[0]

        # From URL path: /api/tenant-slug/...
        path_parts = request.path.split("/")
        if len(path_parts) > 2:
            return path_parts[1]

        return None
