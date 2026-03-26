from django.db.models import QuerySet


def get_tenant_from_request(request):
    """Get tenant from request object"""
    return getattr(request, "tenant", None)


def filter_by_tenant(queryset: QuerySet, request):
    """Filter queryset by current tenant"""
    tenant = get_tenant_from_request(request)
    if tenant and hasattr(queryset.model, "tenant"):
        return queryset.filter(tenant=tenant)
    return queryset


def set_tenant_for_object(obj, request):
    """Set tenant on object before saving"""
    tenant = get_tenant_from_request(request)
    if tenant and hasattr(obj, "tenant"):
        obj.tenant = tenant
    return obj
