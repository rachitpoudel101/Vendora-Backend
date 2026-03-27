from django.contrib import admin
from core.apps.themes.models import ThemeConfiguration


@admin.register(ThemeConfiguration)
class ThemeConfigurationAdmin(admin.ModelAdmin):
    list_display = ("tenant", "primary_color", "sidebar_color", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("tenant__name",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Tenant", {"fields": ("tenant",)}),
        (
            "Colors",
            {
                "fields": (
                    "primary_color",
                    "sidebar_color",
                    "navbar_color",
                    "button_color",
                )
            },
        ),
        # ("Branding", {"fields": ("logo", "font_family")}),
        ("Features", {"fields": ("dark_mode_enabled",)}),
        ("Metadata", {"fields": ("created_at", "updated_at")}),
    )
