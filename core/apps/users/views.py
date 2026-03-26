import traceback

from rest_framework import status, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from core.apps.users.models import Users
from core.apps.users.permissions.permissions import IsAdmin, IsSuperAdmin
from core.apps.users.serializers.serializers import (
    LogoutSerializer,
    SelfAPISerilizer,
    UserCreateSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsSuperAdmin | IsAdmin]
    serializer_class = UserCreateSerializer

    def get_queryset(self):
        """Filter users by current tenant"""
        user = self.request.user
        tenant = getattr(self.request, "tenant", None)

        # If no tenant from middleware, try to get from user
        if not tenant and user and hasattr(user, "tenant"):
            tenant = user.tenant

        queryset = Users.objects.filter(is_super=False, is_deleted=False)

        # Superusers can see all users from all tenants
        if user.is_super or user.is_superuser:
            return queryset

        # Regular users see only users from their tenant
        if tenant:
            queryset = queryset.filter(tenant=tenant)
        else:
            queryset = queryset.none()

        if not user.is_super:
            queryset = queryset.filter(is_super=False)
        if user.role == "admin":
            queryset = queryset.filter(is_super=False)

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(
            {"detail": "User soft deleted (is_deleted=True)"},
            status=status.HTTP_204_NO_CONTENT,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # Use provided tenant or fall back to request tenant
        tenant = validated_data.get("tenant") or getattr(request, "tenant", None)

        user = Users.objects.create_user(
            username=validated_data["username"],
            role=validated_data["role"],
            email=validated_data.get("email", ""),
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            tenant=tenant,
        )
        user.set_password(validated_data.get("password"))
        if user.role == Users.RolesChoices.STAFF:
            user.is_staff = True
        user.save()
        output_serializer = self.get_serializer(user)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        for attr, value in validated_data.items():
            if attr == "password":
                continue
            setattr(instance, attr, value)
        password = validated_data.get("password")
        if password:
            instance.set_password(password)
        if instance.role == Users.RolesChoices.STAFF:
            instance.is_staff = True
        elif instance.role == Users.RolesChoices.ADMIN:
            instance.is_staff = True
        else:
            instance.is_staff = False
        instance.save()
        output_serializer = self.get_serializer(instance)
        return Response(output_serializer.data)


class SelfDetails(ListAPIView):
    queryset = Users.objects.all()
    serializer_class = SelfAPISerilizer

    def list(self, request, *args, **kwargs):
        try:
            user = self.queryset.filter(id=request.user.id).first()
            if not user:
                return Response(
                    {"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.serializer_class(user, context={"request": request})
            data = serializer.data

            return Response(data)
        except Exception as e:
            traceback.print_exc()
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogoutView(APIView):
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        refresh_token = serializer.validated_data["refresh"]

        try:
            token = RefreshToken(refresh_token)
            try:
                token.blacklist()
                return Response(
                    {"detail": "Token blacklisted"},
                    status=status.HTTP_205_RESET_CONTENT,
                )
            except AttributeError:
                return Response(
                    {"detail": "Blacklisting not supported. Check your configuration."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except TokenError:
            return Response(
                {"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserRoleUpdateAPIView(APIView):
    permission_classes = [IsAdmin | IsSuperAdmin]

    def post(self, request, user_id):
        user_id = user_id
        role = request.data.get("role")

        if not user_id or not role:
            return Response(
                {"error": "user_id and role is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = Users.objects.get(id=user_id)
            user.role = role
            user.save()

            return Response(
                {"message": "The user's role is updated"}, status=status.HTTP_200_OK
            )

        except Users.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class RoleConfigView(APIView):
    def get(self, request):
        roles = [choice[0] for choice in Users.RolesChoices.choices]
        return Response({"roles": roles})


class UserRestoreAPIView(APIView):
    permission_classes = [IsAdmin | IsSuperAdmin, IsAuthenticated]

    def post(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id, is_deleted=True)
            user.is_deleted = False
            user.save()
            return Response({"message": "User restored"}, status=status.HTTP_200_OK)
        except Users.DoesNotExist:
            return Response(
                {"error": "User not found or not deleted"},
                status=status.HTTP_404_NOT_FOUND,
            )


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id=None):
        """
        Change password for a user.
        - Superadmin: can change password for any user
        - Tenant admin: can change password for themselves and staff in their tenant
        - Normal user: can only change their own password
        """
        current_user = request.user

        # If no user_id provided, user is changing their own password
        if user_id is None:
            target_user = current_user
        else:
            try:
                target_user = Users.objects.get(id=user_id)
            except Users.DoesNotExist:
                return Response(
                    {"error": "User not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        # Check permissions
        if user_id is not None:  # Admin changing someone else's password
            # Superadmin can change anyone's password
            if current_user.is_superuser or current_user.is_super:
                pass  # Allowed
            # Tenant admin can change password for staff and themselves
            elif current_user.role == "admin" and current_user.tenant:
                if target_user.id == current_user.id:
                    pass  # Admin changing own password
                elif (
                    target_user.role == "staff"
                    and target_user.tenant == current_user.tenant
                ):
                    pass  # Admin changing staff password in same tenant
                else:
                    return Response(
                        {
                            "error": "You don't have permission to change this user's password"
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )
            else:
                return Response(
                    {
                        "error": "You don't have permission to change this user's password"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        new_password = request.data.get("password")
        if not new_password:
            return Response(
                {"error": "Password is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(new_password) < 8:
            return Response(
                {"error": "Password must be at least 8 characters long"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        target_user.set_password(new_password)
        target_user.save()

        return Response(
            {"message": "Password changed successfully"},
            status=status.HTTP_200_OK,
        )
