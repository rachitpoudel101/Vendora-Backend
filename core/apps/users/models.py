from django.contrib.auth.models import AbstractUser
from django.db import models


class Users(AbstractUser):
    class RolesChoices(models.TextChoices):
        ADMIN = "admin"
        STAFF = "staff"
        # CUSTOMER = "customer"

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
        help_text="Tenant this user belongs to",
    )
    role = models.CharField(max_length=50, choices=RolesChoices.choices)
    is_super = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_users",
    )
    is_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
