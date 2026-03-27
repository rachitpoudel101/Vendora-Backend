from django.db import models
from django.core.validators import RegexValidator


class ThemeConfiguration(models.Model):
    """Theme configuration for each tenant"""

    tenant = models.OneToOneField(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="theme",
        help_text="Tenant this theme belongs to",
    )

    # Color fields with hex validation
    hex_validator = RegexValidator(
        regex=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
        message="Enter a valid hex color code (e.g., #FF5733 or #F57)",
    )

    primary_color = models.CharField(
        max_length=7,
        default="#3B82F6",
        validators=[hex_validator],
        help_text="Primary brand color",
    )
    sidebar_color = models.CharField(
        max_length=7,
        default="#1F2937",
        validators=[hex_validator],
        help_text="Sidebar background color",
    )
    navbar_color = models.CharField(
        max_length=7,
        default="#1F2937",
        validators=[hex_validator],
        help_text="Navbar background color",
    )
    button_color = models.CharField(
        max_length=7,
        default="#3B82F6",
        validators=[hex_validator],
        help_text="Button background color",
    )

    # Logo
    logo = models.ImageField(
        upload_to="tenant_logos/",
        null=True,
        blank=True,
        help_text="Tenant logo image",
    )

    # Typography (for future expansion)
    font_family = models.CharField(
        max_length=100,
        default="Inter",
        help_text="Primary font family",
    )

    # Dark mode support (for future expansion)
    dark_mode_enabled = models.BooleanField(
        default=False,
        help_text="Enable dark mode support",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "theme_configurations"
        verbose_name = "Theme Configuration"
        verbose_name_plural = "Theme Configurations"

    def __str__(self):
        return f"Theme for {self.tenant.name}"
