from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('login/', views.custom_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('change-password/', views.change_password, name='change_password'),
    path('download-staff-template/', views.download_staff_template, name='download_staff_template'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
