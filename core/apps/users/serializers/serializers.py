from rest_framework import serializers

from core.apps.users.models import Users
from core.apps.tenants.models import Tenant


class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(required=True)
    tenant = serializers.PrimaryKeyRelatedField(
        queryset=Tenant.objects.all(),
        required=False,
        allow_null=True,
        help_text="Tenant ID to assign to this user",
    )
    tenant_name = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = [
            "id",
            "first_name",
            "last_name",
            "password",
            "username",
            "role",
            "email",
            "tenant",
            "tenant_name",
        ]

    def get_tenant_name(self, obj):
        """Get the tenant name for display"""
        if obj.tenant:
            return obj.tenant.name
        return None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Allow superusers to select any tenant
        request = self.context.get("request")
        if request and (request.user.is_superuser or request.user.is_super):
            self.fields["tenant"].queryset = Tenant.objects.all()
        else:
            # Regular users can only assign their own tenant
            if request and hasattr(request.user, "tenant") and request.user.tenant:
                self.fields["tenant"].queryset = Tenant.objects.filter(
                    id=request.user.tenant.id
                )
            else:
                self.fields["tenant"].queryset = Tenant.objects.none()

    def validate(self, data):
        username = data.get("username")
        if Users.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {"username": "This username is already taken."}
            )
        request = self.context.get("request")
        if request:
            creator = request.user
            new_role = data.get("role")
            is_super = getattr(creator, "is_superuser", False) or getattr(
                creator, "is_super", False
            )

            if new_role == "admin" and not is_super:
                raise serializers.ValidationError(
                    {"role": "Only superadmin can create admin users."}
                )
            if new_role == "staff" and getattr(creator, "role", None) == "admin":
                pass
            elif new_role == "admin" and getattr(creator, "role", None) == "admin":
                raise serializers.ValidationError(
                    {"role": "Admin cannot create another admin."}
                )
            elif (
                new_role == "staff"
                and getattr(creator, "role", None) != "admin"
                and not is_super
            ):
                raise serializers.ValidationError(
                    {"role": "Only admin or superadmin can create staff users."}
                )
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)


class SelfAPISerilizer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = [
            "id",
            "username",
            "role",
            "tenant",
        ]
