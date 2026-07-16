import pandas as pd
from django.db import transaction
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from departments.models import Department
from core.views import IsAdminOrReadOnly
from .models import Student
from .serializers import StudentSerializer
from .filters import StudentFilter


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all().select_related("department")
    serializer_class = StudentSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = StudentFilter
    search_fields = ["enrollment_no", "name", "email", "phone"]
    ordering_fields = ["enrollment_no", "name", "batch", "semester", "created_at"]

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
                return Response(
                    {"detail": "Unsupported file type. Use .csv or .xlsx"}, status=400
                )
        except Exception as e:
            return Response({"detail": f"Could not read file: {e}"}, status=400)

        required_cols = {"enrollment_no", "name", "department_code", "batch"}
        missing = required_cols - set(c.strip() for c in df.columns)
        if missing:
            return Response(
                {"detail": f"Missing required columns: {', '.join(sorted(missing))}"},
                status=400,
            )

        dept_map = {d.code.upper(): d for d in Department.objects.all()}
        results = []
        created, updated, failed = 0, 0, 0

        with transaction.atomic():
            for idx, row in df.iterrows():
                row_num = idx + 2  # account for header row, 1-indexed
                enrollment_no = str(row.get("enrollment_no", "")).strip()
                name = str(row.get("name", "")).strip()
                dept_code = str(row.get("department_code", "")).strip().upper()
                batch = str(row.get("batch", "")).strip()

                if not enrollment_no or not name or not dept_code or not batch:
                    results.append({
                        "row": row_num, "enrollment_no": enrollment_no,
                        "status": "failed", "error": "Missing required field(s)",
                    })
                    failed += 1
                    continue

                department = dept_map.get(dept_code)
                if not department:
                    results.append({
                        "row": row_num, "enrollment_no": enrollment_no,
                        "status": "failed", "error": f"Unknown department_code '{dept_code}'",
                    })
                    failed += 1
                    continue

                semester_raw = str(row.get("semester", "1")).strip()
                try:
                    semester = int(float(semester_raw)) if semester_raw else 1
                except ValueError:
                    semester = 1

                defaults = {
                    "name": name,
                    "department": department,
                    "batch": batch,
                    "semester": semester,
                    "section": str(row.get("section", "")).strip(),
                    "phone": str(row.get("phone", "")).strip(),
                    "email": str(row.get("email", "")).strip(),
                }

                try:
                    obj, was_created = Student.objects.update_or_create(
                        enrollment_no=enrollment_no, defaults=defaults
                    )
                    if was_created:
                        created += 1
                        results.append({"row": row_num, "enrollment_no": enrollment_no, "status": "created"})
                    else:
                        updated += 1
                        results.append({"row": row_num, "enrollment_no": enrollment_no, "status": "updated"})
                except Exception as e:
                    failed += 1
                    results.append({
                        "row": row_num, "enrollment_no": enrollment_no,
                        "status": "failed", "error": str(e),
                    })

        return Response({
            "summary": {
                "total_rows": len(df),
                "created": created,
                "updated": updated,
                "failed": failed,
            },
            "results": results,
        }, status=status.HTTP_200_OK)
