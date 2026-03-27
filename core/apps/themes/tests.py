from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from core.apps.tenants.models import Tenant
from core.apps.themes.models import ThemeConfiguration

User = get_user_model()


class ThemeConfigurationModelTest(TestCase):
    """Test ThemeConfiguration model"""

    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test Tenant",
            slug="test-tenant",
            email="test@example.com",
        )

    def test_theme_creation(self):
        """Test creating a theme configuration"""
        theme = ThemeConfiguration.objects.create(tenant=self.tenant)
        self.assertEqual(theme.tenant, self.tenant)
        self.assertEqual(theme.primary_color, "#3B82F6")
        self.assertEqual(theme.sidebar_color, "#1F2937")

    def test_theme_default_values(self):
        """Test default color values"""
        theme = ThemeConfiguration.objects.create(tenant=self.tenant)
        self.assertEqual(theme.primary_color, "#3B82F6")
        self.assertEqual(theme.sidebar_color, "#1F2937")
        self.assertEqual(theme.navbar_color, "#FFFFFF")
        self.assertEqual(theme.button_color, "#3B82F6")
        self.assertEqual(theme.font_family, "Inter")
        self.assertFalse(theme.dark_mode_enabled)

    def test_theme_one_to_one_relationship(self):
        """Test OneToOne relationship with Tenant"""
        ThemeConfiguration.objects.create(tenant=self.tenant)
        # Should not be able to create another theme for same tenant
        with self.assertRaises(Exception):
            ThemeConfiguration.objects.create(tenant=self.tenant)

    def test_theme_string_representation(self):
        """Test __str__ method"""
        theme = ThemeConfiguration.objects.create(tenant=self.tenant)
        self.assertEqual(str(theme), f"Theme for {self.tenant.name}")

    def test_hex_color_validation(self):
        """Test hex color validation"""
        theme = ThemeConfiguration.objects.create(tenant=self.tenant)
        # Valid hex colors
        theme.primary_color = "#FF0000"
        theme.full_clean()
        theme.save()

        theme.primary_color = "#F00"
        theme.full_clean()
        theme.save()

    def test_invalid_hex_color(self):
        """Test invalid hex color raises validation error"""
        from django.core.exceptions import ValidationError

        theme = ThemeConfiguration.objects.create(tenant=self.tenant)
        theme.primary_color = "invalid"
        with self.assertRaises(ValidationError):
            theme.full_clean()


class ThemeConfigurationAPITest(APITestCase):
    """Test ThemeConfiguration API endpoints"""

    def setUp(self):
        self.client = APIClient()

        # Create tenants
        self.tenant1 = Tenant.objects.create(
            name="Tenant 1",
            slug="tenant-1",
            email="tenant1@example.com",
        )
        self.tenant2 = Tenant.objects.create(
            name="Tenant 2",
            slug="tenant-2",
            email="tenant2@example.com",
        )

        # Create themes
        self.theme1 = ThemeConfiguration.objects.create(
            tenant=self.tenant1,
            primary_color="#FF0000",
        )
        self.theme2 = ThemeConfiguration.objects.create(
            tenant=self.tenant2,
            primary_color="#00FF00",
        )

        # Create users
        self.admin_user = User.objects.create_user(
            username="admin",
            password="testpass123",
            role="admin",
            tenant=self.tenant1,
        )
        self.staff_user = User.objects.create_user(
            username="staff",
            password="testpass123",
            role="staff",
            tenant=self.tenant1,
        )
        self.admin_user2 = User.objects.create_user(
            username="admin2",
            password="testpass123",
            role="admin",
            tenant=self.tenant2,
        )

    def test_get_current_theme_authenticated(self):
        """Test getting current theme when authenticated"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/themes/current/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["primary_color"], "#FF0000")

    def test_get_current_theme_unauthenticated(self):
        """Test getting current theme without authentication"""
        response = self.client.get("/themes/current/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_tenant_isolation_in_list(self):
        """Test that users only see their tenant's theme"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/themes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["primary_color"], "#FF0000")

    def test_admin_can_update_theme(self):
        """Test that admin can update theme"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            f"/themes/{self.theme1.id}/",
            {"primary_color": "#0000FF"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["primary_color"], "#0000FF")

    def test_staff_cannot_update_theme(self):
        """Test that staff cannot update theme"""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.patch(
            f"/themes/{self.theme1.id}/",
            {"primary_color": "#0000FF"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_access_other_tenant_theme(self):
        """Test that admin cannot access other tenant's theme"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f"/themes/{self.theme2.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_multiple_colors(self):
        """Test updating multiple colors at once"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            f"/themes/{self.theme1.id}/",
            {
                "primary_color": "#FF0000",
                "sidebar_color": "#000000",
                "button_color": "#00FF00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["primary_color"], "#FF0000")
        self.assertEqual(response.data["sidebar_color"], "#000000")
        self.assertEqual(response.data["button_color"], "#00FF00")

    def test_update_font_family(self):
        """Test updating font family"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            f"/themes/{self.theme1.id}/",
            {"font_family": "Roboto"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["font_family"], "Roboto")

    def test_toggle_dark_mode(self):
        """Test toggling dark mode"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            f"/themes/{self.theme1.id}/",
            {"dark_mode_enabled": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["dark_mode_enabled"])

    def test_theme_includes_tenant_name(self):
        """Test that theme response includes tenant name"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/themes/current/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["tenant_name"], "Tenant 1")

    def test_invalid_hex_color_rejected(self):
        """Test that invalid hex color is rejected"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            f"/themes/{self.theme1.id}/",
            {"primary_color": "invalid"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_short_hex_color_accepted(self):
        """Test that short hex color format is accepted"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            f"/themes/{self.theme1.id}/",
            {"primary_color": "#F00"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["primary_color"], "#F00")

    def test_superuser_can_access_any_theme(self):
        """Test that superuser can access any theme"""
        superuser = User.objects.create_user(
            username="superuser",
            password="testpass123",
            is_super=True,
            role="admin",
        )
        self.client.force_authenticate(user=superuser)
        response = self.client.get(f"/themes/{self.theme1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_default_theme_for_new_tenant(self):
        """Test creating default theme for new tenant"""
        new_tenant = Tenant.objects.create(
            name="New Tenant",
            slug="new-tenant",
            email="new@example.com",
        )
        theme = ThemeConfiguration.objects.create(tenant=new_tenant)
        self.assertEqual(theme.primary_color, "#3B82F6")
        self.assertEqual(theme.sidebar_color, "#1F2937")

    def test_theme_timestamps(self):
        """Test that timestamps are set correctly"""
        theme = ThemeConfiguration.objects.create(tenant=self.tenant1)
        self.assertIsNotNone(theme.created_at)
        self.assertIsNotNone(theme.updated_at)
        self.assertEqual(theme.created_at, theme.updated_at)

    def test_theme_updated_timestamp_changes(self):
        """Test that updated_at changes when theme is modified"""
        import time

        theme = ThemeConfiguration.objects.create(tenant=self.tenant1)
        created_at = theme.created_at
        time.sleep(0.1)
        theme.primary_color = "#FF0000"
        theme.save()
        self.assertEqual(theme.created_at, created_at)
        self.assertGreater(theme.updated_at, created_at)
