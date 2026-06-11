from django.db import models
from departments.models import Faculty, Department
from halls.models import SeminarHall

class FunctionRequest(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('PENDING_HOD', 'Pending HOD Approval'),
        ('PENDING_MANAGEMENT', 'Pending Management Approval'),
        ('PENDING_PRINCIPAL', 'Pending Principal Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='DRAFT')

    # Step 1 Fields
    function_name = models.CharField(max_length=200)
    function_type = models.CharField(max_length=100)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    number_of_days = models.IntegerField(default=1)
    time_from = models.TimeField()
    time_to = models.TimeField()
    venue = models.ForeignKey(SeminarHall, on_delete=models.SET_NULL, null=True, blank=True)
    type_of_training = models.CharField(max_length=100, blank=True)
    number_of_students = models.IntegerField(default=0)
    class_name = models.CharField(max_length=100, blank=True)
    
    organizer_name = models.CharField(max_length=100)
    organizer_contact = models.CharField(max_length=20, blank=True)
    
    chief_guest_name = models.CharField(max_length=100, blank=True)
    chief_guest_designation = models.CharField(max_length=100, blank=True)
    chief_guest_organization = models.CharField(max_length=200, blank=True)

    @property
    def has_report(self):
        return hasattr(self, 'report')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.function_name} ({self.department.department_code})"
