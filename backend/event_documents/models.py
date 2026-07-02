from django.db import models
from requests.models import FunctionRequest

class EventReport(models.Model):
    function_request = models.OneToOneField(FunctionRequest, on_delete=models.CASCADE, related_name='report')
    dept_ref_no = models.CharField(max_length=100, blank=True)
    objective = models.TextField(blank=True)
    funding_agency = models.CharField(max_length=200, blank=True)
    alumni_contribution = models.CharField(max_length=200, blank=True)
    
    budget_proposed = models.CharField(max_length=50, blank=True, default="-")
    budget_actual = models.CharField(max_length=50, blank=True, default="-")
    
    participants_internal = models.CharField(max_length=100, blank=True)
    participants_external = models.CharField(max_length=100, blank=True)
    
    outcome = models.TextField(blank=True)
    
    # 2 Event Photos directly
    photo_1 = models.ImageField(upload_to='iqac_photos/', null=True, blank=True)
    photo_2 = models.ImageField(upload_to='iqac_photos/', null=True, blank=True)

    # Enclosures mapping text fields just to know what was attached or just storing files
    brochure = models.ImageField(upload_to='brochures/', null=True, blank=True)
    certificate = models.ImageField(upload_to='certificates/', null=True, blank=True)
    feedback_report = models.ImageField(upload_to='feedback/', null=True, blank=True)
    attendance_sheet = models.ImageField(upload_to='attendance/', null=True, blank=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.function_request.function_name}"

class ReportGuest(models.Model):
    event_report = models.ForeignKey(EventReport, on_delete=models.CASCADE, related_name='guests')
    name = models.CharField(max_length=200, blank=True)
    designation = models.CharField(max_length=200, blank=True)
    organization_address = models.TextField(blank=True)
    mobile = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True, null=True)
    topic = models.CharField(max_length=255, blank=True)
