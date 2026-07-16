import django_filters
from .models import Student


class StudentFilter(django_filters.FilterSet):
    department = django_filters.CharFilter(field_name="department__code", lookup_expr="iexact")
    batch = django_filters.CharFilter(field_name="batch", lookup_expr="iexact")
    section = django_filters.CharFilter(field_name="section", lookup_expr="iexact")

    class Meta:
        model = Student
        fields = ["department", "batch", "section", "semester", "is_active"]
