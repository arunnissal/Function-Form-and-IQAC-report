from django.urls import path, include
from rest_framework.routers import DefaultRouter
from function_requirement_system.api.views_users import UserViewSet
from function_requirement_system.api.views import CustomTokenObtainPairView, UserProfileView
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', UserProfileView.as_view(), name='auth_me'),
    path('', include(router.urls)),
]
