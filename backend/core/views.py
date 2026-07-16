from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer, UserCreateSerializer, MeSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and request.user.role == User.Role.ADMIN


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().select_related("department").order_by("username")
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def me(request):
    return Response(MeSerializer(request.user).data)
