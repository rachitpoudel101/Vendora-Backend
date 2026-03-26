from django.test import TestCase
from .models import Tenant


class TenantModelTest(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test Business",
            slug="test-business",
            email="test@example.com",
            phone="1234567890",
            tier="basic",
        )

    def test_tenant_creation(self):
        self.assertEqual(self.tenant.name, "Test Business")
        self.assertTrue(self.tenant.is_active)

    def test_tenant_slug_unique(self):
        with self.assertRaises(Exception):
            Tenant.objects.create(
                name="Another Business",
                slug="test-business",
                email="another@example.com",
            )
