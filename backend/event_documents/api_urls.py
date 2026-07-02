from django.urls import path
from . import api_views

urlpatterns = [
    path('<int:req_id>/', api_views.iqac_report_api, name='api_iqac_report'),
    path('<int:req_id>/generate-pdf/', api_views.generate_iqac_pdf_api, name='api_generate_iqac_pdf'),
]
