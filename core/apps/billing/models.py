from django.db import models

from core.apps.inventory.models import Productstock
from core.apps.users.models import Users


class Bill(models.Model):
    class Meta:
        db_table = "bill"

    class PaymentChoices(models.TextChoices):
        CASH = "cash"
        ONLINE = "online"

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="bills",
        null=True,
        blank=True,
        help_text="Tenant this bill belongs to",
    )
    customer_Name = models.CharField(max_length=50, default=None)
    date = models.DateField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, choices=PaymentChoices.choices)
    actual_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    bill_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    recived_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2)
    billed_by = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="bills", null=True
    )

    def __str__(self):
        return self.customer_Name


class BillingItem(models.Model):
    class Meta:
        db_table = "billing_Items"

    bill_id = models.ForeignKey(
        Bill, on_delete=models.CASCADE, related_name="bill_items", null=True
    )
    product_id = models.ForeignKey(
        Productstock, on_delete=models.CASCADE, related_name="products_bill", null=True
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    unit_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
