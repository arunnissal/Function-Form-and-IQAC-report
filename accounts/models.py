from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('FACULTY', 'Faculty'),
        ('HOD', 'HOD'),
        ('MANAGEMENT', 'Management / AO'),
        ('PRINCIPAL', 'Principal'),
        ('ADMIN', 'System Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='FACULTY')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
