from rest_framework import serializers
from .models import Student


class StudentSerializer(serializers.ModelSerializer):
    department_code = serializers.CharField(source="department.code", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = Student
        fields = [
            "id", "enrollment_no", "name", "department", "department_code",
            "department_name", "batch", "semester", "section", "phone",
            "email", "user_account", "is_active", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_enrollment_no(self, value):
        return value.strip()


class BulkImportRowResultSerializer(serializers.Serializer):
    row = serializers.IntegerField()
    enrollment_no = serializers.CharField(allow_blank=True)
    status = serializers.CharField()
    error = serializers.CharField(required=False, allow_blank=True)
