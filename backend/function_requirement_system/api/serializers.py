from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email
        token['role'] = user.role
        token['name'] = user.get_full_name() or user.username
        token['is_superuser'] = user.is_superuser
        return token

class UserSerializer(serializers.ModelSerializer):
    department = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role', 'is_active', 'department', 'is_superuser']

    def get_department(self, obj):
        if obj.role == 'FACULTY' and hasattr(obj, 'faculty_profile') and obj.faculty_profile.department:
            return obj.faculty_profile.department.department_name
        elif obj.role == 'HOD' and hasattr(obj, 'hod_profile') and obj.hod_profile.department:
            return obj.hod_profile.department.department_name
        return None
