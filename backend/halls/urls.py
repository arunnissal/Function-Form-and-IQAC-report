from django.urls import path, include
from rest_framework.routers import DefaultRouter
from function_requirement_system.api.views_core import SeminarHallViewSet

router = DefaultRouter()
router.register(r'halls', SeminarHallViewSet, basename='hall')

urlpatterns = [
    path('', include(router.urls)),
]
