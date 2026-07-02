from rest_framework import serializers
from requests.models import FunctionRequest
from resources.models import GuestHouseRequirement, RefreshmentRequirement, TransportRequirement, PowerCameraRequirement, MementoRequirement
from departments.models import Faculty, Department
from halls.models import SeminarHall

class GuestHouseRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestHouseRequirement
        exclude = ('function_request',)

class RefreshmentRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefreshmentRequirement
        exclude = ('function_request',)

class TransportRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportRequirement
        exclude = ('function_request',)

class PowerCameraRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PowerCameraRequirement
        exclude = ('function_request',)

class MementoRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = MementoRequirement
        exclude = ('function_request',)

class FunctionRequestSerializer(serializers.ModelSerializer):
    guest_house = GuestHouseRequirementSerializer(read_only=True)
    refreshment = RefreshmentRequirementSerializer(read_only=True)
    transport = TransportRequirementSerializer(read_only=True)
    power_camera = PowerCameraRequirementSerializer(read_only=True)
    memento = MementoRequirementSerializer(read_only=True)
    department_name = serializers.CharField(source='department.department_name', read_only=True)
    venue_name = serializers.CharField(source='venue.name', read_only=True)
    faculty_name = serializers.CharField(source='faculty.user.get_full_name', read_only=True)

    class Meta:
        model = FunctionRequest
        fields = '__all__'
