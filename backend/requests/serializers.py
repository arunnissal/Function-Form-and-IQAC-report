from rest_framework import serializers
from requests.models import FunctionRequest
from resources.models import GuestHouseRequirement, RefreshmentRequirement, TransportRequirement, PowerCameraRequirement, MementoRequirement
from approvals.models import ApprovalLog

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

class ApprovalLogSerializer(serializers.ModelSerializer):
    approver_name = serializers.CharField(source='approver.get_full_name', read_only=True)
    class Meta:
        model = ApprovalLog
        fields = ['id', 'approver_name', 'stage', 'status', 'remarks', 'timestamp']

class FunctionRequestSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source='faculty.user.get_full_name', read_only=True)
    department_code = serializers.CharField(source='department.department_code', read_only=True)
    venue_name = serializers.CharField(source='venue.hall_name', read_only=True)
    
    # Nested serializers
    guest_house = GuestHouseRequirementSerializer()
    refreshment = RefreshmentRequirementSerializer()
    transport = TransportRequirementSerializer()
    power_camera = PowerCameraRequirementSerializer()
    memento = MementoRequirementSerializer()
    approval_logs = ApprovalLogSerializer(many=True, read_only=True)

    class Meta:
        model = FunctionRequest
        fields = '__all__'
        read_only_fields = ('faculty', 'department', 'status', 'created_at', 'updated_at')

    def validate(self, data):
        # Validate capacity
        if 'venue' in data and 'number_of_students' in data:
            venue = data['venue']
            students = data['number_of_students']
            if venue and students > venue.capacity:
                raise serializers.ValidationError({"number_of_students": f"Number of students ({students}) cannot exceed hall capacity ({venue.capacity})."})
        return data

    def create(self, validated_data):
        # Extract nested data
        guest_house_data = validated_data.pop('guest_house')
        refreshment_data = validated_data.pop('refreshment')
        transport_data = validated_data.pop('transport')
        power_camera_data = validated_data.pop('power_camera')
        memento_data = validated_data.pop('memento')

        # Create main request
        function_request = FunctionRequest.objects.create(**validated_data)

        # Create nested models
        GuestHouseRequirement.objects.create(function_request=function_request, **guest_house_data)
        RefreshmentRequirement.objects.create(function_request=function_request, **refreshment_data)
        TransportRequirement.objects.create(function_request=function_request, **transport_data)
        PowerCameraRequirement.objects.create(function_request=function_request, **power_camera_data)
        MementoRequirement.objects.create(function_request=function_request, **memento_data)

        return function_request

    def update(self, instance, validated_data):
        # Extract nested data first to avoid mutating dictionary during iteration
        guest_house_data = validated_data.pop('guest_house', None)
        refreshment_data = validated_data.pop('refreshment', None)
        transport_data = validated_data.pop('transport', None)
        power_camera_data = validated_data.pop('power_camera', None)
        memento_data = validated_data.pop('memento', None)

        # Update main fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Helper to update nested fields
        def update_nested_instance(data, model_class):
            if data is not None:
                nested_instance, _ = model_class.objects.get_or_create(function_request=instance)
                for attr, value in data.items():
                    setattr(nested_instance, attr, value)
                nested_instance.save()

        update_nested_instance(guest_house_data, GuestHouseRequirement)
        update_nested_instance(refreshment_data, RefreshmentRequirement)
        update_nested_instance(transport_data, TransportRequirement)
        update_nested_instance(power_camera_data, PowerCameraRequirement)
        update_nested_instance(memento_data, MementoRequirement)

        return instance
