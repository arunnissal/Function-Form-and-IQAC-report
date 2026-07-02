from rest_framework import serializers
from departments.models import Department
from halls.models import SeminarHall

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class SeminarHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeminarHall
        fields = '__all__'
