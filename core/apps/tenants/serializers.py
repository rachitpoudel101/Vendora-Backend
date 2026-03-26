from rest_framework import serializers
from .models import Tenant


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = [
            "id",
            "name",
            "slug",
            "email",
            "phone",
            "address",
            "subscription_start",
            "subscription_end",
            "is_active",
            "tier",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
