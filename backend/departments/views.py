from rest_framework import viewsets, permissions
from .models import Department
from .serializers import DepartmentSerializer
from core.views import IsAdminOrReadOnly


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrReadOnly]
