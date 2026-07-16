from rest_framework import serializers
from .models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    hod_name = serializers.CharField(source="hod.get_full_name", read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ["id", "code", "name", "hod", "hod_name", "member_count", "created_at"]

    def get_member_count(self, obj):
        return obj.members.count()
