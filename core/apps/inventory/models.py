from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from core.apps.Supliers.models import Supliers


class UnitType(models.Model):
    unit = models.CharField(
        max_length=15, help_text="Name of the unit, e.g., 'Piece', 'Box', 'Carton'."
    )
    description = models.TextField(
        blank=True, null=True, help_text="Optional description of the unit type."
    )
    is_deleted = models.BooleanField(
        default=False, help_text="Indicates if the unit type is deleted (soft delete)."
    )

    def save(self, *args, **kwargs):
        # If a deleted unit with the same name exists, reactivate it
        if self.pk is None:
            existing = UnitType.objects.filter(unit=self.unit, is_deleted=True).first()
            if existing:
                existing.is_deleted = False
                existing.save()
                self.pk = existing.pk  # Use the reactivated unit's pk
                self.is_deleted = False
                return  # Do not create a new row, just update the old one
            self.is_deleted = False
        super().save(*args, **kwargs)

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return self.unit

    class Meta:
        db_table = "unit_type"


class Category(models.Model):
    class Meta:
        db_table = "category"

    name = models.CharField(max_length=100, help_text="Name of the category.")
    is_expired_applicable = models.BooleanField(
        default=False, help_text="Does this category require expiry dates?"
    )
    is_deleted = models.BooleanField(
        default=False, help_text="Indicates if the category is deleted (soft delete)."
    )

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return self.name


class Productstock(models.Model):
    class Meta:
        db_table = "product_stock"

    unit = models.ForeignKey(
        UnitType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Unit type for this product.",
    )
    name = models.CharField(max_length=100, help_text="Product name.")
    product_code = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        help_text="Unique product code.",
    )
    supliers = models.ForeignKey(
        Supliers,
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        blank=True,
        help_text="Supplier for this product.",
    )
    batch_number = models.CharField(
        max_length=100, blank=True, null=True, help_text="Batch number for the product."
    )
    serial_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Serial number for the product.",
    )
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Cost price of the product.",
    )
    stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Current stock quantity.",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        help_text="Category of the product.",
    )
    margin = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Margin for the product.",
    )
    expires_at = models.DateTimeField(
        null=True, blank=True, help_text="Expiry date of the product, if applicable."
    )
    is_deleted = models.BooleanField(
        default=False, help_text="Indicates if the product is deleted (soft delete)."
    )
    base_unit = models.ForeignKey(
        UnitType,
        on_delete=models.CASCADE,
        related_name="products_base_unit",
        null=True,
        blank=True,
        help_text="Base unit type for this product.",
    )

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    @property
    def is_expired(self):
        return self.expires_at and self.expires_at <= timezone.now()

    def clean(self):
        # Cost and margin validation
        if self.cost_price is not None and self.cost_price < 0:
            raise ValidationError("Cost price cannot be negative.")
        if self.margin is not None and self.margin < 0:
            raise ValidationError("Margin cannot be negative.")

        # Serial number uniqueness validation (when provided)
        if self.serial_number:
            existing_serial = Productstock.objects.filter(
                serial_number=self.serial_number, is_deleted=False
            ).exclude(pk=self.pk if self.pk else None)

            if existing_serial.exists():
                raise ValidationError(
                    {"serial_number": "This serial number already exists."}
                )

        # Expiry validation based on category
        if (
            self.category
            and self.category.is_expired_applicable
            and not self.expires_at
        ):
            raise ValidationError(
                {
                    "expires_at": "This product must have an expiry date because its category is expired applicable."
                }
            )

        # If category is not expired applicable, clear product expiry
        if self.category and not self.category.is_expired_applicable:
            self.expires_at = None

    def generate_batch_number(self):
        """Generate batch number in format YYYYMMDD-XXX where XXX is sequential counter"""
        from datetime import datetime

        today = datetime.now()
        date_prefix = today.strftime("%Y%m%d")

        # Find existing batch numbers for today
        existing_batches = Productstock.objects.filter(
            batch_number__startswith=date_prefix, is_deleted=False
        ).exclude(pk=self.pk if self.pk else None)

        # Generate next sequential number
        if existing_batches.exists():
            # Extract the highest counter for today
            counters = []
            for batch in existing_batches:
                try:
                    counter_part = batch.batch_number.split("-")[-1]
                    counters.append(int(counter_part))
                except (ValueError, IndexError):
                    continue

            next_counter = max(counters) + 1 if counters else 1
        else:
            next_counter = 1

        return f"{date_prefix}-{next_counter:03d}"

    def save(self, *args, **kwargs):
        if not self.batch_number:
            self.batch_number = self.generate_batch_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class UnitTypeConfigurations(models.Model):
    class Meta:
        db_table = "unit_configurations"

    product = models.ForeignKey(
        Productstock,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Product for which this configuration applies.",
    )
    unit_type = models.ForeignKey(
        UnitType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="configUnit_type",
        help_text="Unit type for conversion.",
    )
    conversion_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1,
        help_text="Number of conversion units per unit type.",
    )
    conversion_unit_name = models.ForeignKey(
        UnitType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="conversion_unit_configurations",
        help_text="Unit name to convert to, e.g., 'pieces', 'boxes'.",
    )
    is_deleted = models.BooleanField(
        default=False,
        help_text="Indicates if the configuration is deleted (soft delete).",
    )

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return f"{self.conversion_per_unit} {self.unit_type.unit if self.unit_type else 'Unknown'}"
