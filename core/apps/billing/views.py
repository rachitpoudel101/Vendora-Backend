from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core.apps.billing.models import Bill
from core.apps.billing.serializers.serializers import BillSerializer
from core.apps.users.permissions.permissions import IsAdmin, Isstaff, IsSuperAdmin


class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer
    permission_classes = [ IsSuperAdmin | IsAdmin | Isstaff]

    def get_queryset(self):
        """Filter bills by current tenant"""
        tenant = getattr(self.request, 'tenant', None)
        
        # If no tenant from middleware, try to get from user
        if not tenant and self.request.user and hasattr(self.request.user, "tenant"):
            tenant = self.request.user.tenant
        
        if tenant:
            return Bill.objects.filter(tenant=tenant)
        return Bill.objects.none()

    def perform_create(self, serializer):
        """Set tenant when creating bill"""
        tenant = getattr(self.request, 'tenant', None)
        if not tenant and self.request.user and hasattr(self.request.user, "tenant"):
            tenant = self.request.user.tenant
        serializer.save(tenant=tenant)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        items_data = validated_data.pop("bill_items", [])

        from core.apps.billing.models import BillingItem

        tenant = getattr(request, 'tenant', None)
        if not tenant and request.user and hasattr(request.user, "tenant"):
            tenant = request.user.tenant
        
        bill = Bill.objects.create(tenant=tenant, **validated_data)
        for item_data in items_data:
            product = item_data["product_id"]
            quantity = item_data["quantity"]
            if quantity < 0:
                return self._error_response("Quantity cannot be negative.")
            if product.stock < quantity:
                return self._error_response(
                    f"Not enough stock for product '{product.name}'. Available: {product.stock}, Requested: {quantity}"
                )
            product.stock -= quantity
            if product.stock < 0:
                return self._error_response(
                    f"Stock for product '{product.name}' cannot be negative after billing."
                )
            product.save()
            if (
                item_data.get("unit_price", 0) < 0
                or item_data.get("selling_price", 0) < 0
                or item_data.get("discount_amount", 0) < 0
                or item_data.get("unit_total", 0) < 0
            ):
                return self._error_response("Amounts cannot be negative.")
            item_data.pop("bill_id", None)
            BillingItem.objects.create(bill_id=bill, **item_data)
        output_serializer = self.get_serializer(bill)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def _error_response(self, message):
        return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
