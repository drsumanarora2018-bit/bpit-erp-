from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    department_code = serializers.CharField(source="department.code", read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "last_name", "email", "phone",
            "role", "department", "department_name", "department_code",
            "is_active_member", "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "last_name", "email", "phone",
            "role", "department", "password",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class MeSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "last_name", "email",
            "role", "department", "department_name",
        ]
