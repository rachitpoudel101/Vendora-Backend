from rest_framework import serializers

from core.apps.billing.models import Bill, BillingItem
from core.apps.inventory.serializers.serializers import ProductStockSerializer


class BillingItemSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductStockSerializer.Meta.model.objects.all()
    )
    bill_id = serializers.PrimaryKeyRelatedField(
        queryset=Bill.objects.all(), required=False
    )

    class Meta:
        model = BillingItem
        fields = [
            "bill_id",
            "product_id",
            "quantity",
            "unit_price",
            "discount_amount",
            "unit_total",
        ]


class BillSerializer(serializers.ModelSerializer):
    items = BillingItemSerializer(
        many=True, source="bill_items"
    )  # changed source to 'bill_items'

    class Meta:
        model = Bill
        fields = [
            "id",
            "customer_Name",
            "date",
            "payment_method",
            "billed_by",
            "vat_amount",
            "tax_amount",
            "bill_discount",
            "actual_amount",
            "recived_amount",
            "grand_total",
            "items",
        ]
