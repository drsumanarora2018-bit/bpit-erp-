import pandas as pd
from decimal import Decimal
from django.db import transaction
from django.db.models import Sum, Avg, Count, Q
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from core.views import IsAdminOrReadOnly
from students.models import Student
from .models import Subject, Result, grade_from_percentage
from .serializers import SubjectSerializer, ResultSerializer, MarksheetSerializer
from .filters import ResultFilter


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all().select_related("department")
    serializer_class = SubjectSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["department", "semester"]
    search_fields = ["code", "name"]


class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all().select_related("student", "subject", "student__department")
    serializer_class = ResultSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ResultFilter
    search_fields = ["student__enrollment_no", "student__name", "subject__code"]
    ordering_fields = ["academic_year", "created_at"]

    @action(detail=False, methods=["post"], url_path="bulk-import")
    def bulk_import(self, request):
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response({"detail": "No file uploaded. Use form field 'file'."}, status=400)

        filename = file_obj.name.lower()
        try:
            if filename.endswith(".csv"):
                df = pd.read_csv(file_obj, dtype=str, keep_default_na=False)
            elif filename.endswith((".xlsx", ".xls")):
                df = pd.read_excel(file_obj, dtype=str)
                df = df.fillna("")
            else:
                return Response({"detail": "Unsupported file type. Use .csv or .xlsx"}, status=400)
        except Exception as e:
            return Response({"detail": f"Could not read file: {e}"}, status=400)

        required_cols = {"enrollment_no", "subject_code", "academic_year", "marks_obtained"}
        missing = required_cols - set(c.strip() for c in df.columns)
        if missing:
            return Response(
                {"detail": f"Missing required columns: {', '.join(sorted(missing))}"}, status=400
            )

        student_map = {s.enrollment_no: s for s in Student.objects.all()}
        subject_map = {s.code.upper(): s for s in Subject.objects.all()}
        results_log = []
        created, updated, failed = 0, 0, 0

        with transaction.atomic():
            for idx, row in df.iterrows():
                row_num = idx + 2
                enrollment_no = str(row.get("enrollment_no", "")).strip()
                subject_code = str(row.get("subject_code", "")).strip().upper()
                academic_year = str(row.get("academic_year", "")).strip()
                marks_raw = str(row.get("marks_obtained", "")).strip()
                max_marks_raw = str(row.get("max_marks", "100")).strip() or "100"
                exam_type = str(row.get("exam_type", "THEORY")).strip().upper() or "THEORY"

                if not enrollment_no or not subject_code or not academic_year or not marks_raw:
                    results_log.append({"row": row_num, "enrollment_no": enrollment_no,
                                         "status": "failed", "error": "Missing required field(s)"})
                    failed += 1
                    continue

                student = student_map.get(enrollment_no)
                if not student:
                    results_log.append({"row": row_num, "enrollment_no": enrollment_no,
                                         "status": "failed", "error": "Unknown student enrollment_no"})
                    failed += 1
                    continue

                subject = subject_map.get(subject_code)
                if not subject:
                    results_log.append({"row": row_num, "enrollment_no": enrollment_no,
                                         "status": "failed", "error": f"Unknown subject_code '{subject_code}'"})
                    failed += 1
                    continue

                try:
                    marks_obtained = Decimal(marks_raw)
                    max_marks = Decimal(max_marks_raw)
                except Exception:
                    results_log.append({"row": row_num, "enrollment_no": enrollment_no,
                                         "status": "failed", "error": "Invalid marks value"})
                    failed += 1
                    continue

                if exam_type not in Result.ExamType.values:
                    exam_type = "THEORY"

                try:
                    obj, was_created = Result.objects.update_or_create(
                        student=student, subject=subject, exam_type=exam_type,
                        academic_year=academic_year,
                        defaults={"marks_obtained": marks_obtained, "max_marks": max_marks},
                    )
                    if was_created:
                        created += 1
                        results_log.append({"row": row_num, "enrollment_no": enrollment_no, "status": "created"})
                    else:
                        updated += 1
                        results_log.append({"row": row_num, "enrollment_no": enrollment_no, "status": "updated"})
                except Exception as e:
                    failed += 1
                    results_log.append({"row": row_num, "enrollment_no": enrollment_no,
                                         "status": "failed", "error": str(e)})

        return Response({
            "summary": {"total_rows": len(df), "created": created, "updated": updated, "failed": failed},
            "results": results_log,
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="marksheet")
    def marksheet(self, request):
        enrollment_no = request.query_params.get("enrollment_no")
        academic_year = request.query_params.get("academic_year")
        if not enrollment_no:
            return Response({"detail": "enrollment_no query param is required"}, status=400)

        try:
            student = Student.objects.select_related("department").get(enrollment_no=enrollment_no)
        except Student.DoesNotExist:
            return Response({"detail": "Student not found"}, status=404)

        qs = Result.objects.filter(student=student).select_related("subject")
        if academic_year:
            qs = qs.filter(academic_year=academic_year)

        if not qs.exists():
            return Response({"detail": "No results found for this student/year"}, status=404)

        subjects_data = []
        total_obtained = Decimal("0")
        total_max = Decimal("0")
        for r in qs:
            subjects_data.append({
                "subject_code": r.subject.code,
                "subject_name": r.subject.name,
                "credits": r.subject.credits,
                "exam_type": r.exam_type,
                "marks_obtained": r.marks_obtained,
                "max_marks": r.max_marks,
                "grade": r.grade,
            })
            total_obtained += r.marks_obtained
            total_max += r.max_marks

        percentage = (total_obtained / total_max * 100) if total_max > 0 else Decimal("0")
        overall_grade = grade_from_percentage(float(percentage))

        data = {
            "student_enrollment_no": student.enrollment_no,
            "student_name": student.name,
            "department_code": student.department.code,
            "batch": student.batch,
            "academic_year": academic_year or "All",
            "subjects": subjects_data,
            "total_obtained": total_obtained,
            "total_max": total_max,
            "percentage": round(percentage, 2),
            "overall_grade": overall_grade,
        }
        return Response(MarksheetSerializer(data).data)

    @action(detail=False, methods=["get"], url_path="class-summary")
    def class_summary(self, request):
        department = request.query_params.get("department")
        batch = request.query_params.get("batch")
        academic_year = request.query_params.get("academic_year")
        subject_code = request.query_params.get("subject")

        qs = Result.objects.select_related("student", "subject")
        if department:
            qs = qs.filter(student__department__code__iexact=department)
        if batch:
            qs = qs.filter(student__batch__iexact=batch)
        if academic_year:
            qs = qs.filter(academic_year=academic_year)
        if subject_code:
            qs = qs.filter(subject__code__iexact=subject_code)

        if not qs.exists():
            return Response({"detail": "No results found for given filters"}, status=404)

        total_count = qs.count()
        pass_count = qs.exclude(grade="F").count()
        fail_count = total_count - pass_count
        avg_pct = qs.annotate().aggregate(
            avg_marks=Avg("marks_obtained"),
        )

        # Compute average percentage manually since max_marks can vary
        pct_sum = Decimal("0")
        for r in qs:
            if r.max_marks > 0:
                pct_sum += (r.marks_obtained / r.max_marks * 100)
        avg_percentage = round(pct_sum / total_count, 2) if total_count else 0

        grade_distribution = dict(
            qs.values("grade").annotate(count=Count("id")).values_list("grade", "count")
        )

        return Response({
            "filters": {"department": department, "batch": batch, "academic_year": academic_year, "subject": subject_code},
            "total_entries": total_count,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "pass_percentage": round(pass_count / total_count * 100, 2) if total_count else 0,
            "average_percentage": avg_percentage,
            "grade_distribution": grade_distribution,
        })
