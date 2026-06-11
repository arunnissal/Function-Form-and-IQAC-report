from django.db import models
from requests.models import FunctionRequest

class EventReport(models.Model):
    function_request = models.OneToOneField(FunctionRequest, on_delete=models.CASCADE, related_name='report')
    brochure = models.FileField(upload_to='brochures/', null=True, blank=True)
    photos = models.FileField(upload_to='photos/', null=True, blank=True)
    attendance_sheet = models.FileField(upload_to='attendance/', null=True, blank=True)
    feedback_report = models.FileField(upload_to='feedback/', null=True, blank=True)
    outcome = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.function_request.function_name}"
