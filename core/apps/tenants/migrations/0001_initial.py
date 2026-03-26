# Generated migration for Tenant model

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Tenant",
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
                    "name",
                    models.CharField(
                        help_text="Business name", max_length=255, unique=True
                    ),
                ),
                (
                    "slug",
                    models.SlugField(help_text="URL-friendly identifier", unique=True),
                ),
                (
                    "email",
                    models.EmailField(
                        help_text="Primary contact email", max_length=254
                    ),
                ),
                ("phone", models.CharField(blank=True, max_length=20, null=True)),
                ("address", models.TextField(blank=True, null=True)),
                ("subscription_start", models.DateField(auto_now_add=True)),
                ("subscription_end", models.DateField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "tier",
                    models.CharField(
                        choices=[
                            ("basic", "Basic"),
                            ("professional", "Professional"),
                            ("enterprise", "Enterprise"),
                        ],
                        default="basic",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "tenants",
                "ordering": ["-created_at"],
            },
        ),
    ]
