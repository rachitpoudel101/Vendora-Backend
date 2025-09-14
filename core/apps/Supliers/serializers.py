from rest_framework import serializers

from core.apps.Supliers.models import Supliers


class SupliersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supliers
        fields = ["id", "name", "phone", "address"]


class SupliersCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
    address = serializers.CharField(required=True)

    class Meta:
        model = Supliers
        fields = ["id", "name", "phone", "address"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        return Supliers.objects.create(**validated_data)

    # def validate_name(self, value):
    #     if Supliers.objects.filter(name=value, is_deleted=False).exists():
    #         raise serializers.ValidationError("Supliers with this name already exists.")
    #     return value

    # def update(self, instance, validated_data):
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #     instance.save()
    #     return instance
