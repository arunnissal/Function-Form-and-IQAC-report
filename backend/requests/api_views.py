from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import FunctionRequest
from .serializers import FunctionRequestSerializer
from departments.models import Faculty
from approvals.models import ApprovalLog
from departments.models import Faculty

class IsFacultyUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['FACULTY', 'HOD']

class FunctionRequestViewSet(viewsets.ModelViewSet):
    serializer_class = FunctionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = FunctionRequest.objects.all().order_by('-created_at')
        
        if self.request.query_params.get('all_approved') == 'true':
            return queryset.filter(status='APPROVED')
            
        if user.role == 'FACULTY':
            try:
                return queryset.filter(faculty=user.faculty_profile)
            except:
                return FunctionRequest.objects.none()
        elif user.role == 'HOD':
            try:
                return queryset.filter(department=user.hod_profile.department)
            except:
                return FunctionRequest.objects.none()
        return queryset

    @action(detail=False, methods=['get'])
    def queue(self, request):
        user = request.user
        queryset = FunctionRequest.objects.none()
        
        if user.role == 'HOD':
            try:
                queryset = FunctionRequest.objects.filter(department=user.hod_profile.department, status='PENDING_HOD')
            except:
                pass
        elif user.role == 'DEAN_COMPUTING':
            computing_depts = ['CSE', 'CSE(CS)', 'AIDS', 'IT', 'CSBS']
            queryset = FunctionRequest.objects.filter(
                department__department_code__in=computing_depts, 
                status='PENDING_DEAN'
            )
        elif user.role == 'MANAGEMENT':
            queryset = FunctionRequest.objects.filter(status='PENDING_MANAGEMENT')
        elif user.role == 'PRINCIPAL':
            queryset = FunctionRequest.objects.filter(status='PENDING_PRINCIPAL')
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        user = self.request.user
        try:
            faculty = user.faculty_profile
        except:
            # Fallback for HOD
            faculty = user.hod_profile.department.faculty_set.first() # Mock, should be robust in real app
            if not faculty:
                from departments.models import Faculty
                faculty = Faculty.objects.create(user=user, department=user.hod_profile.department, faculty_id="HOD01")
        
        dept = faculty.department
        serializer.save(faculty=faculty, department=dept, status='PENDING_HOD')

    def update(self, request, *args, **kwargs):
        # Prevent updates to existing requests by faculty (Lock rule)
        if request.user.role in ['FACULTY']:
            return Response({"detail": "You cannot edit a submitted request."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        req = self.get_object()
        role = request.user.role
        remarks = request.data.get('remarks', '')

        new_status = ''
        if role == 'HOD' and req.status == 'PENDING_HOD':
            computing_depts = ['CSE', 'CSE(CS)', 'AIDS', 'IT', 'CSBS']
            if req.department.department_code.upper() in computing_depts:
                new_status = 'PENDING_DEAN'
            else:
                new_status = 'PENDING_MANAGEMENT'
        elif role == 'DEAN_COMPUTING' and req.status == 'PENDING_DEAN':
            new_status = 'PENDING_MANAGEMENT'
        elif role == 'MANAGEMENT' and req.status == 'PENDING_MANAGEMENT':
            new_status = 'PENDING_PRINCIPAL'
        elif role == 'PRINCIPAL' and req.status == 'PENDING_PRINCIPAL':
            new_status = 'APPROVED'
        else:
            return Response({"detail": "You cannot approve this request at its current stage."}, status=status.HTTP_403_FORBIDDEN)

        req.status = new_status
        req.save()

        ApprovalLog.objects.create(
            function_request=req,
            approver=request.user,
            stage=role,
            status='APPROVED',
            remarks=remarks
        )
        return Response({"status": "approved", "new_status": new_status})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        req = self.get_object()
        role = request.user.role
        remarks = request.data.get('remarks', '')

        # Basic permission check
        if role not in ['HOD', 'DEAN_COMPUTING', 'MANAGEMENT', 'PRINCIPAL']:
            return Response({"detail": "Not authorized to reject."}, status=status.HTTP_403_FORBIDDEN)

        req.status = 'REJECTED'
        req.save()

        ApprovalLog.objects.create(
            function_request=req,
            approver=request.user,
            stage=role,
            status='REJECTED',
            remarks=remarks
        )
        return Response({"status": "rejected"})

    @action(detail=True, methods=['post'])
    def cancel_request(self, request, pk=None):
        req = self.get_object()
        role = request.user.role
        remarks = request.data.get('remarks', 'Cancelled due to emergency')

        if role not in ['MANAGEMENT', 'PRINCIPAL'] and not request.user.is_superuser:
            return Response({"detail": "Not authorized to cancel requests."}, status=status.HTTP_403_FORBIDDEN)

        req.status = 'REJECTED'  # Or create a 'CANCELLED' status
        req.save()

        ApprovalLog.objects.create(
            function_request=req,
            approver=request.user,
            stage=role,
            status='CANCELLED',
            remarks=remarks
        )
        return Response({"status": "cancelled", "detail": "Request has been forcefully cancelled.", "new_status": "REJECTED"})
