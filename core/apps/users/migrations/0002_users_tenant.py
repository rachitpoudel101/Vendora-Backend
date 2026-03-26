# Generated migration to add tenant field to Users model

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tenants", "0001_initial"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="users",
            name="tenant",
            field=models.ForeignKey(
                blank=True,
                help_text="Tenant this user belongs to",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="users",
                to="tenants.tenant",
            ),
        ),
    ]
