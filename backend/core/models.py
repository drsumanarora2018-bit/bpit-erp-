from django.contrib.auth.models import AbstractUser
from django.db import models


class Department(models.Model):
    """Academic department, e.g. CSE, IT, ECE, EEE, AI&DS."""
    code = models.CharField(max_length=10, unique=True, help_text="e.g. CSE, IT, ECE")
    name = models.CharField(max_length=150, help_text="e.g. Computer Science & Engineering")
    hod = models.ForeignKey(
        "User", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="headed_department",
        limit_choices_to={"role": "HOD"},
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class User(AbstractUser):
    """Custom user with a role and optional department affiliation."""

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrator"
        HOD = "HOD", "Head of Department"
        FACULTY = "FACULTY", "Faculty"
        STUDENT = "STUDENT", "Student"
        ACCOUNTS = "ACCOUNTS", "Accounts / Admin Staff"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    department = models.ForeignKey(
        Department, null=True, blank=True, on_delete=models.SET_NULL, related_name="members"
    )
    phone = models.CharField(max_length=15, blank=True)
    enrollment_no = models.CharField(
        max_length=30, blank=True, null=True, unique=True,
        help_text="Only applicable for students"
    )
    is_active_employee = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"
