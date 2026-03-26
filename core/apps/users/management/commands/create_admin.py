from django.core.management.base import BaseCommand

from core.apps.users.models import Users
from core.apps.tenants.models import Tenant

print("create_admin command module loaded")


class Command(BaseCommand):
    help = "Create an initial admin user"

    def handle(self, *args, **kwargs):
        admin_email = "superuser@superuser.com"
        admin_password = "superuser"
        admin_username = "superuser"

        # Create or get default tenant
        default_tenant, created = Tenant.objects.get_or_create(
            slug="default",
            defaults={
                "name": "Default Tenant",
                "email": admin_email,
                "is_active": True,
                "tier": "enterprise",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Default tenant created"))

        if not Users.objects.filter(username=admin_username).exists():
            Users.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password,
                is_super=True,
                role="admin",
                tenant=default_tenant,
            )
            self.stdout.write(self.style.SUCCESS("Admin user created successfully"))
        else:
            self.stdout.write(self.style.WARNING("Admin user already exists"))
