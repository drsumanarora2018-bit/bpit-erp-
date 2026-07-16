from django.db import models


class Student(models.Model):
    class Semester(models.IntegerChoices):
        SEM1 = 1, "Semester 1"
        SEM2 = 2, "Semester 2"
        SEM3 = 3, "Semester 3"
        SEM4 = 4, "Semester 4"
        SEM5 = 5, "Semester 5"
        SEM6 = 6, "Semester 6"
        SEM7 = 7, "Semester 7"
        SEM8 = 8, "Semester 8"

    enrollment_no = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)
    department = models.ForeignKey(
        "departments.Department", on_delete=models.PROTECT, related_name="students"
    )
    batch = models.CharField(max_length=15, help_text="e.g. 2024-28")
    semester = models.IntegerField(choices=Semester.choices, default=Semester.SEM1)
    section = models.CharField(max_length=5, blank=True, default="")
    phone = models.CharField(max_length=15, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    user_account = models.OneToOneField(
        "core.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_profile",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["department__code", "batch", "section", "enrollment_no"]

    def __str__(self):
        return f"{self.enrollment_no} - {self.name}"
