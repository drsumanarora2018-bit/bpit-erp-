from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "department", "is_active_member", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        ("ERP Info", {"fields": ("role", "department", "phone", "is_active_member")}),
    )


admin.site.register(User, CustomUserAdmin)
