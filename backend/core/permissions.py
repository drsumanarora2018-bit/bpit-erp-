from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Full access: Admin only."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "ADMIN")


class IsAdminOrHOD(permissions.BasePermission):
    """Admin or HOD (e.g. can manage users within their own department)."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ("ADMIN", "HOD")
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Anyone authenticated can read; only Admin can write."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role == "ADMIN"
