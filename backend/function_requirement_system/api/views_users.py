from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db import transaction
from departments.models import Department, Faculty, HOD
from .serializers import UserSerializer
import pandas as pd

User = get_user_model()

class IsSuperuserOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_superuser or request.user.role == 'MANAGEMENT')

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'HOD':
            dept = user.hod_profile.department
            faculty_users = Faculty.objects.filter(department=dept).select_related('user')
            return User.objects.filter(id__in=[f.user.id for f in faculty_users])
        elif user.is_superuser or user.role == 'MANAGEMENT':
            return User.objects.exclude(username__in=['admin', 'admin@drngpit.ac.in'])
        return User.objects.none()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        if not request.user.is_superuser and request.user.role != 'MANAGEMENT':
            return Response({'detail': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)
        
        email = request.data.get('email')
        position = request.data.get('position')
        dept_id = request.data.get('department')
        
        if not email or not position or not dept_id:
            return Response({'detail': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
            
        if not email.endswith('@drngpit.ac.in'):
            return Response({'detail': 'Mail id must end with @drngpit.ac.in'}, status=status.HTTP_400_BAD_REQUEST)
            
        if User.objects.filter(username=email).exists():
            return Response({'detail': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
        dept = Department.objects.get(id=dept_id)
        role_map = {'Staff': 'FACULTY', 'HOD': 'HOD'}
        new_role = role_map.get(position, 'FACULTY')
        
        user = User.objects.create(
            username=email,
            email=email,
            role=new_role,
            is_active=True
        )
        user.set_password(email.split('@')[0])
        user.save()
        
        if new_role == 'FACULTY':
            Faculty.objects.create(user=user, department=dept, designation='Staff')
        elif new_role == 'HOD':
            HOD.objects.create(user=user, department=dept)
            
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        if not request.user.is_superuser and request.user.role != 'MANAGEMENT':
            return Response({'detail': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)
            
        user_to_edit = self.get_object()
        position = request.data.get('position')
        dept_id = request.data.get('department')
        
        if user_to_edit.is_superuser or user_to_edit.role in ['DEAN_COMPUTING', 'PRINCIPAL']:
            return Response({'detail': 'Cannot edit high-level users'}, status=status.HTTP_403_FORBIDDEN)
            
        dept = Department.objects.get(id=dept_id)
        role_map = {'Staff': 'FACULTY', 'HOD': 'HOD'}
        new_role = role_map.get(position, 'FACULTY')
        
        user_to_edit.role = new_role
        user_to_edit.save()
        
        Faculty.objects.filter(user=user_to_edit).delete()
        HOD.objects.filter(user=user_to_edit).delete()
        
        if new_role == 'FACULTY':
            Faculty.objects.create(user=user_to_edit, department=dept, designation='Staff')
        elif new_role == 'HOD':
            HOD.objects.create(user=user_to_edit, department=dept)
            
        serializer = self.get_serializer(user_to_edit)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[IsSuperuserOnly])
    def bulk_add(self, request):
        excel_file = request.FILES.get('excel_file')
        if not excel_file:
            return Response({'detail': 'Please upload an Excel file.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            df = pd.read_excel(excel_file)
            required_cols = ['Full Name', 'Email', 'Department Code', 'Position']
            if not all(col in df.columns for col in required_cols):
                return Response({'detail': f"Excel must contain: {', '.join(required_cols)}"}, status=status.HTTP_400_BAD_REQUEST)
                
            success_count = 0
            error_count = 0
            
            with transaction.atomic():
                for index, row in df.iterrows():
                    full_name = str(row.get('Full Name', '')).strip()
                    staff_email = str(row.get('Email', '')).strip()
                    dept_code = str(row.get('Department Code', '')).strip()
                    position = str(row.get('Position', '')).strip()
                    
                    if not staff_email or pd.isna(staff_email) or staff_email == 'nan': continue
                    if not staff_email.endswith('@drngpit.ac.in'):
                        error_count += 1
                        continue
                    if User.objects.filter(username=staff_email).exists():
                        error_count += 1
                        continue
                        
                    dept = Department.objects.filter(department_code__iexact=dept_code).first()
                    if not dept:
                        error_count += 1
                        continue
                        
                    role_map = {'Staff': 'FACULTY', 'HOD': 'HOD'}
                    new_role = role_map.get(position, 'FACULTY')
                    
                    first_name = full_name.split()[0] if full_name else ''
                    last_name = ' '.join(full_name.split()[1:]) if full_name and len(full_name.split()) > 1 else ''
                    
                    user = User.objects.create(
                        username=staff_email,
                        email=staff_email,
                        first_name=first_name,
                        last_name=last_name,
                        role=new_role,
                        is_active=True
                    )
                    user.set_password(staff_email.split('@')[0])
                    user.save()
                    
                    if new_role == 'FACULTY':
                        Faculty.objects.create(user=user, department=dept, designation='Staff')
                    elif new_role == 'HOD':
                        HOD.objects.create(user=user, department=dept)
                        
                    success_count += 1
                    
            return Response({'detail': f'Successfully imported {success_count} users. Failed/Skipped: {error_count}'})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not current_password or not new_password:
            return Response({'detail': 'Both current and new passwords are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(current_password):
            return Response({'detail': 'Incorrect current password.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        
        # update_session_auth_hash is typically needed for session auth to not log the user out,
        # but since we are using simple JWT/Token (presumably), it might not be strictly necessary here, 
        # but Django handles it gracefully.
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, user)

        return Response({'detail': 'Password changed successfully.'})

    @action(detail=True, methods=['post'], permission_classes=[IsSuperuserOnly])
    def reset_password(self, request, pk=None):
        user = self.get_object()
        # Reset password to the part of the email before @
        default_password = user.email.split('@')[0]
        user.set_password(default_password)
        user.save()
        return Response({'detail': f'Password successfully reset to default ({default_password}).'})

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_superuser and request.user.role != 'MANAGEMENT':
            return Response({'detail': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
