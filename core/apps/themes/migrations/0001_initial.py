# Generated migration for theme app

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("tenants", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ThemeConfiguration",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "primary_color",
                    models.CharField(
                        default="#3B82F6",
                        help_text="Primary brand color",
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Enter a valid hex color code (e.g., #FF5733 or #F57)",
                                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                            )
                        ],
                    ),
                ),
                (
                    "sidebar_color",
                    models.CharField(
                        default="#1F2937",
                        help_text="Sidebar background color",
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Enter a valid hex color code (e.g., #FF5733 or #F57)",
                                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                            )
                        ],
                    ),
                ),
                (
                    "navbar_color",
                    models.CharField(
                        default="#FFFFFF",
                        help_text="Navbar background color",
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Enter a valid hex color code (e.g., #FF5733 or #F57)",
                                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                            )
                        ],
                    ),
                ),
                (
                    "button_color",
                    models.CharField(
                        default="#3B82F6",
                        help_text="Button background color",
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Enter a valid hex color code (e.g., #FF5733 or #F57)",
                                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                            )
                        ],
                    ),
                ),
                (
                    "logo",
                    models.ImageField(
                        blank=True,
                        help_text="Tenant logo image",
                        null=True,
                        upload_to="tenant_logos/",
                    ),
                ),
                (
                    "font_family",
                    models.CharField(
                        default="Inter",
                        help_text="Primary font family",
                        max_length=100,
                    ),
                ),
                (
                    "dark_mode_enabled",
                    models.BooleanField(
                        default=False, help_text="Enable dark mode support"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True),
                ),
                (
                    "tenant",
                    models.OneToOneField(
                        help_text="Tenant this theme belongs to",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="theme",
                        to="tenants.tenant",
                    ),
                ),
            ],
            options={
                "verbose_name": "Theme Configuration",
                "verbose_name_plural": "Theme Configurations",
                "db_table": "theme_configurations",
            },
        ),
    ]
