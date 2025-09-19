from rest_framework import serializers
from django.utils import timezone

from core.apps.inventory.models import (
    Category,
    Productstock,
    UnitType,
    UnitTypeConfigurations,
)


class UnitTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitType
        fields = ["id", "unit", "description"]
        read_only_fields = ["id"]

    def validate(self, data):
        unit = data.get("unit")
        if (
            UnitType.objects.filter(unit=unit)
            .exclude(id=getattr(self.instance, "id", None))
            .exists()
        ):
            raise serializers.ValidationError(
                {"unit": "This unit name already exists."}
            )
        return data


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "is_expired_applicable",
        ]
        read_only_fields = ["id"]

    def validate(self, data):
        name = data.get("name")
        if (
            Category.objects.filter(name=name, is_deleted=False)
            .exclude(id=getattr(self.instance, "id", None))
            .exists()
        ):
            raise serializers.ValidationError(
                {"name": "This category name is already taken."}
            )
        return data

    def get_supliers_name(self, obj):
        return (
            obj.supliers.name if obj.supliers and not obj.supliers.is_deleted else None
        )


class ProductStockSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    supliers_name = serializers.SerializerMethodField()
    unit_name = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    base_unit_name = serializers.SerializerMethodField()

    class Meta:
        model = Productstock
        fields = [
            "id",
            "category",
            "category_name",
            "product_code",
            "name",
            "unit",
            "unit_name",
            "base_unit",
            "base_unit_name",
            "supliers",
            "supliers_name",
            "batch_number",
            "serial_number",
            "cost_price",
            "margin",
            "stock",
            "expires_at",
            "is_expired",
        ]
        read_only_fields = [
            "id",
            "category_name",
            "supliers_name",
            "unit_name",
            "base_unit_name",
            "is_expired",
            "batch_number",
            "expires_at",
        ]
        extra_kwargs = {
            "supliers": {"required": True},
            "cost_price": {"required": True},
            "margin": {"required": True},
            "stock": {"required": True},
            "category": {"required": True},
            "unit": {"required": True},
            "base_unit": {"required": True},  # Made base_unit required
            "serial_number": {"required": False},
        }

    def validate(self, data):
        unit = data.get("unit")
        if not unit:
            raise serializers.ValidationError(
                {"unit": "Unit is required for the product."}
            )
        base_unit = data.get("base_unit")
        if not base_unit:
            raise serializers.ValidationError(
                {"base_unit": "Base unit is required for the product."}
            )
        return data

    def get_category_name(self, obj):
        return (
            obj.category.name
            if getattr(obj, "category", None)
            and not getattr(obj.category, "is_deleted", False)
            else None
        )

    def get_supliers_name(self, obj):
        return (
            obj.supliers.name
            if getattr(obj, "supliers", None)
            and not getattr(obj.supliers, "is_deleted", False)
            else None
        )

    def get_unit_name(self, obj):
        return obj.unit.unit if getattr(obj, "unit", None) else None

    def get_is_expired(self, obj):
        if getattr(obj, "expires_at", None):
            return obj.expires_at <= timezone.now()
        return False

    def get_base_unit_name(self, obj):
        return (
            obj.base_unit.unit
            if getattr(obj, "base_unit", None)
            and not getattr(obj.base_unit, "is_deleted", False)
            else None
        )


class UnitTypeConfigurationsSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    base_unit_name = serializers.CharField(source="base_unit.unit", read_only=True)
    conversion_unit_name_display = serializers.CharField(
        source="conversion_unit_name.unit", read_only=True
    )

    class Meta:
        model = UnitTypeConfigurations
        fields = [
            "id",
            "product",
            "product_name",
            "base_unit",
            "base_unit_name",
            "conversion_per_unit",
            "conversion_unit_name",
            "conversion_unit_name_display",
        ]
        read_only_fields = [
            "id",
            "product_name",
            "base_unit_name",
            "conversion_unit_name_display",
        ]
