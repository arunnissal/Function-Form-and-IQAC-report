from rest_framework import viewsets, permissions
from departments.models import Department
from halls.models import SeminarHall
from .serializers_core import DepartmentSerializer, SeminarHallSerializer

class IsManagementOrAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role in ['MANAGEMENT', 'ADMIN']

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsManagementOrAdminOrReadOnly]

class SeminarHallViewSet(viewsets.ModelViewSet):
    queryset = SeminarHall.objects.all()
    serializer_class = SeminarHallSerializer
    permission_classes = [IsManagementOrAdminOrReadOnly]
