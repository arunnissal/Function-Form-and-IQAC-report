from django.urls import path
from . import views

urlpatterns = [
    path('fill/<int:req_id>/', views.fill_iqac_report, name='fill_iqac_report'),
    path('generate-pdf/<int:req_id>/', views.generate_iqac_pdf, name='generate_iqac_pdf'),
]
