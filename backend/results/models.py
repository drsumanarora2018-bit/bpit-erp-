from django.db import models


def grade_from_percentage(pct):
    if pct >= 90:
        return "O"
    if pct >= 80:
        return "A+"
    if pct >= 70:
        return "A"
    if pct >= 60:
        return "B+"
    if pct >= 50:
        return "B"
    if pct >= 40:
        return "C"
    return "F"


class Subject(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150)
    department = models.ForeignKey(
        "departments.Department", on_delete=models.CASCADE, related_name="subjects"
    )
    semester = models.IntegerField()
    credits = models.PositiveSmallIntegerField(default=4)

    class Meta:
        ordering = ["department__code", "semester", "code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Result(models.Model):
    class ExamType(models.TextChoices):
        INTERNAL = "INTERNAL", "Internal"
        EXTERNAL = "EXTERNAL", "External"
        PRACTICAL = "PRACTICAL", "Practical"
        THEORY = "THEORY", "Theory"

    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="results"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="results"
    )
    academic_year = models.CharField(max_length=15, help_text="e.g. 2025-26")
    exam_type = models.CharField(max_length=15, choices=ExamType.choices, default=ExamType.THEORY)
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)
    max_marks = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    grade = models.CharField(max_length=3, blank=True)
    remarks = models.CharField(max_length=100, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "subject", "exam_type", "academic_year")
        ordering = ["-academic_year", "student__enrollment_no", "subject__code"]

    def save(self, *args, **kwargs):
        if self.max_marks and self.max_marks > 0:
            pct = float(self.marks_obtained) / float(self.max_marks) * 100
            self.grade = grade_from_percentage(pct)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.enrollment_no} - {self.subject.code} - {self.marks_obtained}/{self.max_marks}"
