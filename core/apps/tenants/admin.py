from django.contrib import admin
from .models import Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "email", "tier", "is_active", "created_at"]
    list_filter = ["is_active", "tier", "created_at"]
    search_fields = ["name", "email", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at"]
