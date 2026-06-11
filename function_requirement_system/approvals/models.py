from django.db import models
from django.conf import settings
from requests.models import FunctionRequest

class ApprovalLog(models.Model):
    function_request = models.ForeignKey(FunctionRequest, on_delete=models.CASCADE, related_name='approval_logs')
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    stage = models.CharField(max_length=30)
    status = models.CharField(max_length=20)
    remarks = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.function_request.function_name} - {self.stage} - {self.status}"
