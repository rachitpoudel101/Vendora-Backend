from rest_framework import serializers
from core.apps.themes.models import ThemeConfiguration


class ThemeConfigurationSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source="tenant.name", read_only=True)
    logo_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ThemeConfiguration
        fields = [
            "id",
            "tenant",
            "tenant_name",
            "primary_color",
            "sidebar_color",
            "navbar_color",
            "button_color",
            "logo",
            "logo_url",
            "font_family",
            "dark_mode_enabled",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "tenant",
            "tenant_name",
            "logo_url",
            "created_at",
            "updated_at",
        ]

    def get_logo_url(self, obj):
        """Return full URL for logo if it exists"""
        if obj.logo:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None
