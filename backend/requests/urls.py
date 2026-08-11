from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import FunctionRequestViewSet

router = DefaultRouter()
router.register(r'requests', FunctionRequestViewSet, basename='request')

urlpatterns = [
    path('', include(router.urls)),
]
