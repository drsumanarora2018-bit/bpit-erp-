from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Department, User


class DepartmentSerializer(serializers.ModelSerializer):
    hod_name = serializers.CharField(source="hod.get_full_name", read_only=True, default="")
    member_count = serializers.IntegerField(source="members.count", read_only=True)

    class Meta:
        model = Department
        fields = ["id", "code", "name", "hod", "hod_name", "member_count", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    department_code = serializers.CharField(source="department.code", read_only=True, default="")

    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "last_name", "email", "role",
            "department", "department_code", "phone", "enrollment_no",
            "is_active_employee", "is_active", "date_joined",
        ]
        read_only_fields = ["date_joined"]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "last_name", "email", "password",
            "role", "department", "phone", "enrollment_no",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Adds role/name/department info directly into the JWT payload and login response."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["full_name"] = user.get_full_name() or user.username
        token["department"] = user.department.code if user.department else None
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data
