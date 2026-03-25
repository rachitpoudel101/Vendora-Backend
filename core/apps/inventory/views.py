from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.apps.inventory.models import (
    Category,
    Productstock,
    UnitType,
    UnitTypeConfigurations,
)
from core.apps.inventory.serializers.serializers import (
    CategorySerializer,
    ProductStockSerializer,
    UnitTypeConfigurationsSerializer,
    UnitTypeSerializer,
)
from core.apps.users.permissions.permissions import IsAdmin, IsSuperAdmin


class UnitTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product units.
    Only SuperAdmin and Admin can create/update/delete.
    """

    queryset = UnitType.objects.filter(is_deleted=False)
    serializer_class = UnitTypeSerializer
    permission_classes = [IsSuperAdmin | IsAdmin]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        """
        Optionally filter units by unit name.
        Example: /units/?unit=kg
        """
        queryset = super().get_queryset()
        unit = self.request.query_params.get("unit")
        if unit:
            queryset = queryset.filter(unit__icontains=unit)
        return queryset


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product categories.
    Only SuperAdmin and Admin can create/update/delete.
    """

    queryset = Category.objects.filter(is_deleted=False)
    serializer_class = CategorySerializer
    permission_classes = [IsSuperAdmin | IsAdmin]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        """
        Optionally filter categories by supliers or expired_applicable flag.
        Example: /api/categories/?is_expired_applicable=true
        """
        queryset = super().get_queryset()
        is_expired_applicable = self.request.query_params.get("is_expired_applicable")
        if is_expired_applicable is not None:
            queryset = queryset.filter(
                is_expired_applicable=is_expired_applicable.lower() == "true"
            )
        return queryset


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products.
    SuperAdmin, Admin, and Staff can access.
    """

    queryset = Productstock.objects.filter(is_deleted=False)
    serializer_class = ProductStockSerializer
    permission_classes = [IsSuperAdmin | IsAdmin]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        """
        Optionally filter products by category or supliers.
        Example: /api/products/?category=1&supliers=2
        """
        queryset = super().get_queryset()
        category = self.request.query_params.get("category")
        supliers = self.request.query_params.get("supliers")

        if category:
            queryset = queryset.filter(category_id=category)
        if supliers:
            queryset = queryset.filter(supliers_id=supliers)

        return queryset

    @action(detail=True, methods=["post"], url_path="validate")
    def validate_product(self, request, pk=None):
        """
        Custom action to validate a product.
        """
        product = self.get_object()
        from django.utils import timezone

        errors = {}

        # Expiry check
        is_expired = product.expires_at and product.expires_at <= timezone.now()

        # Cost and margin validation
        if product.cost_price is not None and product.cost_price < 0:
            errors["cost_price"] = "Cost price cannot be negative."
        if product.margin is not None and product.margin < 0:
            errors["margin"] = "Margin cannot be negative."

        # Serial number uniqueness validation
        if product.serial_number:
            existing_serial = Productstock.objects.filter(
                serial_number=product.serial_number, is_deleted=False
            ).exclude(pk=product.pk if product.pk else None)
            if existing_serial.exists():
                errors["serial_number"] = "This serial number already exists."

        # Expiry validation based on category
        if (
            product.category
            and product.category.is_expired_applicable
            and not product.expires_at
        ):
            errors["expires_at"] = (
                "This product must have an expiry date because its category is expired applicable."
            )
        if product.category and not product.category.is_expired_applicable:
            product.expires_at = None

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                "is_expired": is_expired,
                "batch_number": product.batch_number,
                "message": "Product validated successfully.",
            }
        )

    def get_category_name(self, obj):
        return (
            obj.category.name if obj.category and not obj.category.is_deleted else None
        )

    def get_supliers_name(self, obj):
        return (
            obj.supliers.name if obj.supliers and not obj.supliers.is_deleted else None
        )

    def get_unit_name(self, obj):
        return obj.unit.unit if obj.unit else None


class UnitTypeConfigurationsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing unit type configurations.
    Only SuperAdmin and Admin can create/update/delete.
    """

    queryset = UnitTypeConfigurations.objects.filter(is_deleted=False)
    serializer_class = UnitTypeConfigurationsSerializer
    permission_classes = [IsSuperAdmin | IsAdmin]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        """
        Optionally filter configurations by product or unit type.
        Example: /api/unit-configurations/?product=1&unit_type=2
        """
        queryset = super().get_queryset()
        product = self.request.query_params.get("product")
        unit_type = self.request.query_params.get("unit_type")

        if product:
            queryset = queryset.filter(product_id=product)
        if unit_type:
            queryset = queryset.filter(unit_type_id=unit_type)

        return queryset
