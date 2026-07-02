from django.db import models

class SeminarHall(models.Model):
    hall_name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    location = models.CharField(max_length=200)
    facilities = models.TextField(blank=True)

    def __str__(self):
        return f"{self.hall_name} ({self.capacity} seats)"
