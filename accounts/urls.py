from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('login/', views.custom_login, name='login'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('change-password-first-time/', views.change_password_first_time, name='change_password_first_time'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
