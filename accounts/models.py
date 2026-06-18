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
    
    # New Auth & Security Fields
    first_login_completed = models.BooleanField(default=False)
    password_setup_token = models.CharField(max_length=100, blank=True, null=True)
    password_setup_token_expiry = models.DateTimeField(blank=True, null=True)
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
