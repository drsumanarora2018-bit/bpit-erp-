from django.db import models


class Department(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=150)
    hod = models.ForeignKey(
        "core.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="headed_department",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"
