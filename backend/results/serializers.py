from rest_framework import serializers
from .models import Subject, Result


class SubjectSerializer(serializers.ModelSerializer):
    department_code = serializers.CharField(source="department.code", read_only=True)

    class Meta:
        model = Subject
        fields = ["id", "code", "name", "department", "department_code", "semester", "credits"]


class ResultSerializer(serializers.ModelSerializer):
    student_enrollment_no = serializers.CharField(source="student.enrollment_no", read_only=True)
    student_name = serializers.CharField(source="student.name", read_only=True)
    subject_code = serializers.CharField(source="subject.code", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        model = Result
        fields = [
            "id", "student", "student_enrollment_no", "student_name",
            "subject", "subject_code", "subject_name", "academic_year",
            "exam_type", "marks_obtained", "max_marks", "grade", "remarks",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "grade", "created_at", "updated_at"]


class MarksheetSubjectSerializer(serializers.Serializer):
    subject_code = serializers.CharField()
    subject_name = serializers.CharField()
    credits = serializers.IntegerField()
    exam_type = serializers.CharField()
    marks_obtained = serializers.DecimalField(max_digits=6, decimal_places=2)
    max_marks = serializers.DecimalField(max_digits=6, decimal_places=2)
    grade = serializers.CharField()


class MarksheetSerializer(serializers.Serializer):
    student_enrollment_no = serializers.CharField()
    student_name = serializers.CharField()
    department_code = serializers.CharField()
    batch = serializers.CharField()
    academic_year = serializers.CharField()
    subjects = MarksheetSubjectSerializer(many=True)
    total_obtained = serializers.DecimalField(max_digits=8, decimal_places=2)
    total_max = serializers.DecimalField(max_digits=8, decimal_places=2)
    percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    overall_grade = serializers.CharField()
