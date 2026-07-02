from django.urls import path
from . import views

urlpatterns = [
    path('manage/', views.manage_halls, name='manage_halls'),
    path('availability/', views.hall_availability, name='hall_availability'),
]
