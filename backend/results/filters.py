import django_filters
from .models import Result


class ResultFilter(django_filters.FilterSet):
    department = django_filters.CharFilter(field_name="student__department__code", lookup_expr="iexact")
    batch = django_filters.CharFilter(field_name="student__batch", lookup_expr="iexact")
    subject = django_filters.CharFilter(field_name="subject__code", lookup_expr="iexact")
    student_enrollment = django_filters.CharFilter(field_name="student__enrollment_no", lookup_expr="iexact")

    class Meta:
        model = Result
        fields = ["department", "batch", "subject", "student_enrollment", "academic_year", "exam_type"]
