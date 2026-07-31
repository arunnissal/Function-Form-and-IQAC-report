from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter
from .views import CustomTokenObtainPairView, UserProfileView
from .views_users import UserViewSet
from .views_core import DepartmentViewSet, SeminarHallViewSet
from requests.api_views import FunctionRequestViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'halls', SeminarHallViewSet, basename='hall')
router.register(r'requests', FunctionRequestViewSet, basename='request')

urlpatterns = [
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', UserProfileView.as_view(), name='auth_me'),
    path('', include(router.urls)),
]
