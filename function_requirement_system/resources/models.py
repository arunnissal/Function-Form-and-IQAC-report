from django.db import models
from requests.models import FunctionRequest

class GuestHouseRequirement(models.Model):
    function_request = models.OneToOneField(FunctionRequest, on_delete=models.CASCADE, related_name='guest_house')
    required = models.BooleanField(default=False)
    number_of_persons = models.IntegerField(default=0, null=True, blank=True)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)

class RefreshmentRequirement(models.Model):
    function_request = models.OneToOneField(FunctionRequest, on_delete=models.CASCADE, related_name='refreshment')
    tea_required = models.BooleanField(default=False)
    coffee_required = models.BooleanField(default=False)
    snacks_required = models.BooleanField(default=False)
    veg_lunch_count = models.IntegerField(default=0)
    non_veg_lunch_count = models.IntegerField(default=0)
    tiffin_count = models.IntegerField(default=0)
    required_time = models.TimeField(null=True, blank=True)
    payment_through = models.CharField(max_length=50, choices=(('ASSOCIATION', 'Association Account'), ('INSTITUTION', 'Institution Account')), blank=True)

class TransportRequirement(models.Model):
    function_request = models.OneToOneField(FunctionRequest, on_delete=models.CASCADE, related_name='transport')
    required = models.BooleanField(default=False)
    date = models.DateField(null=True, blank=True)
    pickup_location = models.CharField(max_length=200, blank=True)
    pickup_time = models.TimeField(null=True, blank=True)
    drop_time = models.TimeField(null=True, blank=True)
    pickup_person_name = models.CharField(max_length=100, blank=True)
    pickup_person_contact = models.CharField(max_length=20, blank=True)

class PowerCameraRequirement(models.Model):
    function_request = models.OneToOneField(FunctionRequest, on_delete=models.CASCADE, related_name='power_camera')
    mic_required = models.BooleanField(default=False)
    mic_type = models.CharField(max_length=100, blank=True)
    number_of_mics = models.IntegerField(default=0)
    ac_required = models.BooleanField(default=False)
    projector_required = models.BooleanField(default=False)
    laptop_required = models.BooleanField(default=False)
    photographer_required = models.BooleanField(default=False)
    photographer_type = models.CharField(max_length=50, choices=(('LAB_TECHNICIAN', 'Lab Technician'), ('OFFICIAL', 'Official Photographer')), blank=True)

class MementoRequirement(models.Model):
    function_request = models.OneToOneField(FunctionRequest, on_delete=models.CASCADE, related_name='memento')
    required = models.BooleanField(default=False)
    honorarium_worth = models.CharField(max_length=100, blank=True)
    quantity = models.IntegerField(default=0)
    dias_seats = models.IntegerField(default=0)
    audience_seats = models.IntegerField(default=0)
    table_cloths = models.IntegerField(default=0)
    reception_items = models.TextField(blank=True)
