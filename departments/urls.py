from django.urls import path
from . import views

urlpatterns = [
    path('manage/', views.manage_departments, name='manage_departments'),
]
