from django.urls import path, include
from rest_framework.routers import DefaultRouter
from function_requirement_system.api.views_core import DepartmentViewSet

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')

urlpatterns = [
    path('', include(router.urls)),
]
