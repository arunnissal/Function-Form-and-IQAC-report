from django.db import models
from django.conf import settings

class Department(models.Model):
    department_name = models.CharField(max_length=100)
    department_code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.department_name

class HOD(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hod_profile')
    department = models.OneToOneField(Department, on_delete=models.CASCADE)

    def __str__(self):
        return f"HOD - {self.department.department_code}"

class Faculty(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='faculty_profile')
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    designation = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.department.department_code}"
