from django.urls import path
from . import views

urlpatterns = [
    path('queue/', views.approval_queue, name='approval_queue'),
    path('<int:req_id>/', views.request_detail, name='request_detail'),
    path('<int:req_id>/edit/', views.edit_request, name='edit_request'),
]
