from django.db import models


class Tenant(models.Model):
    """Multi-tenant model to isolate data per client"""

    name = models.CharField(max_length=255, unique=True, help_text="Business name")
    slug = models.SlugField(unique=True, help_text="URL-friendly identifier")
    email = models.EmailField(help_text="Primary contact email")
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # Subscription details
    subscription_start = models.DateField(auto_now_add=True)
    subscription_end = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # Pricing tier
    TIER_CHOICES = [
        ("basic", "Basic"),
        ("professional", "Professional"),
        ("enterprise", "Enterprise"),
    ]
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default="basic")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tenants"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
