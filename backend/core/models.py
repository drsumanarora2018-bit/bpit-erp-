from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrator"
        FACULTY = "FACULTY", "Faculty"
        STUDENT = "STUDENT", "Student"
        STAFF = "STAFF", "Staff"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STAFF)
    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members",
    )
    phone = models.CharField(max_length=15, blank=True, default="")
    is_active_member = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
