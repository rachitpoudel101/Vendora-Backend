from django.db import models


class Supliers(models.Model):
    class Meta:
        db_table = "supliers"

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="suppliers",
        null=True,
        blank=True,
        help_text="Tenant this supplier belongs to",
    )
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    is_deleted = models.BooleanField(default=False)

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return self.name
