from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import FunctionRequest
from .serializers import FunctionRequestSerializer
from approvals.models import ApprovalLog
from .utils import check_double_booking
from .permissions import IsFacultyOwner, IsHODDepartment, IsDeanComputing, IsManagementAO, IsPrincipal

def check_unauthorized_edits(user_role, existing_data, incoming_data):
    """
    Returns a list of unauthorized fields that the user tried to modify,
    based on the college responsibility-based editing policy.
    """
    changed_blocked_fields = []
    
    logistics_nested = {'guest_house', 'refreshment', 'power_camera', 'memento', 'transport'}
    academic_main = {
        'function_name', 'function_type', 'start_date', 'end_date', 'number_of_days',
        'time_from', 'time_to', 'type_of_training', 'number_of_students', 'class_name',
        'organizer_name', 'organizer_contact', 'chief_guest_name', 'chief_guest_designation',
        'chief_guest_organization'
    }
    
    def normalize(val):
        if val is None or val == 'None' or val == '':
            return ''
        return str(val).strip()

    if user_role == 'HOD':
        # Blocked: venue, and all logistics nested models
        if 'venue' in incoming_data:
            existing_venue = existing_data.get('venue')
            incoming_venue = incoming_data.get('venue')
            if normalize(existing_venue) != normalize(incoming_venue):
                changed_blocked_fields.append('venue')
                
        for nested in logistics_nested:
            if nested in incoming_data and isinstance(incoming_data[nested], dict):
                exist_nested = existing_data.get(nested) or {}
                inc_nested = incoming_data[nested]
                for key, val in inc_nested.items():
                    if key != 'id':
                        exist_val = exist_nested.get(key)
                        if normalize(exist_val) != normalize(val):
                            changed_blocked_fields.append(f"{nested}.{key}")

    elif user_role == 'DEAN_COMPUTING':
        # Dean can ONLY edit: function_name, function_type, type_of_training
        # Blocked main academic fields except function_name, function_type, type_of_training
        blocked_main = academic_main - {'function_name', 'function_type', 'type_of_training'}
        blocked_main.add('venue')
        
        for field in blocked_main:
            if field in incoming_data:
                exist_val = existing_data.get(field)
                inc_val = incoming_data.get(field)
                if normalize(exist_val) != normalize(inc_val):
                    changed_blocked_fields.append(field)
                    
        for nested in logistics_nested:
            if nested in incoming_data and isinstance(incoming_data[nested], dict):
                exist_nested = existing_data.get(nested) or {}
                inc_nested = incoming_data[nested]
                for key, val in inc_nested.items():
                    if key != 'id':
                        exist_val = exist_nested.get(key)
                        if normalize(exist_val) != normalize(val):
                            changed_blocked_fields.append(f"{nested}.{key}")
                            
    elif user_role == 'MANAGEMENT':
        # Management must NOT edit academic main fields
        for field in academic_main:
            if field in incoming_data:
                exist_val = existing_data.get(field)
                inc_val = incoming_data.get(field)
                if normalize(exist_val) != normalize(inc_val):
                    changed_blocked_fields.append(field)
                    
    elif user_role == 'PRINCIPAL':
        # Principal can edit NOTHING
        all_main = academic_main | {'venue'}
        for field in all_main:
            if field in incoming_data:
                exist_val = existing_data.get(field)
                inc_val = incoming_data.get(field)
                if normalize(exist_val) != normalize(inc_val):
                    changed_blocked_fields.append(field)
        for nested in logistics_nested:
            if nested in incoming_data and isinstance(incoming_data[nested], dict):
                exist_nested = existing_data.get(nested) or {}
                inc_nested = incoming_data[nested]
                for key, val in inc_nested.items():
                    if key != 'id':
                        exist_val = exist_nested.get(key)
                        if normalize(exist_val) != normalize(val):
                            changed_blocked_fields.append(f"{nested}.{key}")
                            
    return changed_blocked_fields

class FunctionRequestViewSet(viewsets.ModelViewSet):
    serializer_class = FunctionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsFacultyOwner()]
        return super().get_permissions()

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
                # Can only access department requests
                return queryset.filter(department=user.hod_profile.department)
            except:
                return FunctionRequest.objects.none()
        elif user.role == 'DEAN_COMPUTING':
            # Can only access requests from CSE, CSE(CS), AIDS, IT, CSBS
            computing_depts = ['CSE', 'CSE(CS)', 'AIDS', 'IT', 'CSBS']
            return queryset.filter(department__department_code__in=computing_depts)
        elif user.role == 'PRINCIPAL':
            return queryset
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
            queryset = FunctionRequest.objects.filter(status__in=['PENDING_MANAGEMENT', 'PENDING_FINAL_CONFIRMATION'])
        elif user.role == 'PRINCIPAL':
            queryset = FunctionRequest.objects.filter(status='PENDING_PRINCIPAL')
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        user = self.request.user
        faculty = user.faculty_profile
        dept = faculty.department
        status_val = self.request.data.get('status', 'PENDING_HOD')
        if status_val not in ['DRAFT', 'PENDING_HOD']:
            status_val = 'PENDING_HOD'
            
        serializer.save(faculty=faculty, department=dept, status=status_val)
        
        # Log to audit trail
        ApprovalLog.objects.create(
            function_request=serializer.instance,
            approver=user,
            stage='FACULTY',
            status='SUBMITTED' if status_val == 'PENDING_HOD' else 'DRAFT',
            remarks='Draft created' if status_val == 'DRAFT' else 'Request submitted to HOD'
        )

        if status_val == 'PENDING_HOD':
            from .notifications import send_hod_submission_notification
            send_hod_submission_notification(serializer.instance)

    def update(self, request, *args, **kwargs):
        req = self.get_object()
        user = request.user
        
        # Enforce server-side role-based editing constraints
        if user.role == 'FACULTY':
            if req.faculty != user.faculty_profile:
                return Response({"detail": "You do not own this request."}, status=status.HTTP_403_FORBIDDEN)
            if req.status not in ['DRAFT', 'RETURNED_FOR_CORRECTION']:
                return Response({"detail": "You can only edit draft requests or requests returned for correction."}, status=status.HTTP_403_FORBIDDEN)
        elif user.role == 'HOD':
            if req.department != user.hod_profile.department:
                return Response({"detail": "You cannot edit requests from other departments."}, status=status.HTTP_403_FORBIDDEN)
            if req.status != 'PENDING_HOD':
                return Response({"detail": "You can only edit requests during HOD review stage."}, status=status.HTTP_403_FORBIDDEN)
        elif user.role == 'DEAN_COMPUTING':
            computing_depts = ['CSE', 'CSE(CS)', 'AIDS', 'IT', 'CSBS']
            if req.department.department_code.upper() not in computing_depts:
                return Response({"detail": "You cannot edit requests outside Computing cluster."}, status=status.HTTP_403_FORBIDDEN)
            if req.status != 'PENDING_DEAN':
                return Response({"detail": "You can only edit requests during Dean review stage."}, status=status.HTTP_403_FORBIDDEN)
        elif user.role == 'MANAGEMENT':
            if req.status not in ['PENDING_MANAGEMENT', 'PENDING_FINAL_CONFIRMATION']:
                return Response({"detail": "You can only edit requests during Management review stages."}, status=status.HTTP_403_FORBIDDEN)
        elif user.role == 'PRINCIPAL':
            if req.status != 'PENDING_PRINCIPAL':
                return Response({"detail": "You can only edit requests during Principal review stage."}, status=status.HTTP_403_FORBIDDEN)
        elif not user.is_superuser:
            return Response({"detail": "Not authorized to modify this request."}, status=status.HTTP_403_FORBIDDEN)

        # Enforce responsibility-based editing policy (validate field-level changes)
        existing_serializer = self.get_serializer(req)
        unauthorized_changes = check_unauthorized_edits(user.role, existing_serializer.data, request.data)
        if unauthorized_changes:
            return Response(
                {"detail": f"You do not have permission to modify these responsibility-blocked fields: {', '.join(unauthorized_changes)}"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Capture previous state of fields to track modifications
        old_values = {}
        fields_to_track = [
            'function_name', 'function_type', 'start_date', 'end_date', 'time_from', 'time_to',
            'venue', 'number_of_students', 'class_name', 'organizer_name', 'organizer_contact',
            'chief_guest_name', 'chief_guest_designation', 'chief_guest_organization'
        ]
        for field in fields_to_track:
            old_values[field] = getattr(req, field)
            
        is_resubmit = request.data.get('resubmit', False)
        
        serializer = self.get_serializer(req, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()
        
        # Determine changed fields for audit trail
        changes = []
        for field in fields_to_track:
            old_val = old_values[field]
            new_val = getattr(updated_instance, field)
            
            if field == 'venue':
                old_id = old_val.id if old_val else None
                new_id = new_val.id if new_val else None
                if old_id != new_id:
                    old_name = old_val.hall_name if old_val else 'None'
                    new_name = new_val.hall_name if new_val else 'None'
                    changes.append(f"Venue (from '{old_name}' to '{new_name}')")
            else:
                if str(old_val) != str(new_val):
                    field_name = field.replace('_', ' ').title()
                    changes.append(f"{field_name} (from '{old_val}' to '{new_val}')")
                    
        # Log to timeline audit trail if fields changed by an approver
        if changes and user.role != 'FACULTY':
            remarks = request.data.get('remarks', 'Administrative modification')
            change_description = ", ".join(changes)
            
            ApprovalLog.objects.create(
                function_request=updated_instance,
                approver=user,
                stage=user.role,
                status='MODIFIED',
                remarks=f"Modified: {change_description}. Remarks: {remarks}"
            )
            
        if is_resubmit and user.role == 'FACULTY':
            old_status = updated_instance.status
            if old_status == 'RETURNED_FOR_CORRECTION':
                new_status = updated_instance.previous_status or 'PENDING_HOD'
                updated_instance.status = new_status
                updated_instance.previous_status = None
            else:
                new_status = 'PENDING_HOD'
                updated_instance.status = new_status
            updated_instance.save()
            
            # Log resubmission
            ApprovalLog.objects.create(
                function_request=updated_instance,
                approver=user,
                stage='FACULTY',
                status='RESUBMITTED',
                remarks='Request resubmitted after changes'
            )
            
            from .notifications import send_resubmission_notification
            send_resubmission_notification(updated_instance, new_status)
            
        return Response(self.get_serializer(updated_instance).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        req = self.get_object()
        role = request.user.role
        remarks = request.data.get('remarks', '')

        # Strictly verify HOD, Dean, Management, Principal role permissions using custom DRF classes
        if role == 'HOD':
            perm = IsHODDepartment()
        elif role == 'DEAN_COMPUTING':
            perm = IsDeanComputing()
        elif role == 'MANAGEMENT':
            perm = IsManagementAO()
        elif role == 'PRINCIPAL':
            perm = IsPrincipal()
        else:
            return Response({"detail": "Not authorized to approve requests."}, status=status.HTTP_403_FORBIDDEN)

        if not perm.has_object_permission(request, self, req):
            return Response({"detail": "Permission denied for this request context."}, status=status.HTTP_403_FORBIDDEN)

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
            # Check double booking
            if check_double_booking(req.venue, req.start_date, req.end_date, req.time_from, req.time_to, exclude_req_id=req.id):
                return Response({"detail": "This seminar hall is already booked for the selected date and time range."}, status=status.HTTP_400_BAD_REQUEST)
            new_status = 'PENDING_PRINCIPAL'
        elif role == 'PRINCIPAL' and req.status == 'PENDING_PRINCIPAL':
            # Check double booking again before principal approval
            if check_double_booking(req.venue, req.start_date, req.end_date, req.time_from, req.time_to, exclude_req_id=req.id):
                return Response({"detail": "This seminar hall is already booked for the selected date and time range."}, status=status.HTTP_400_BAD_REQUEST)
            new_status = 'PENDING_FINAL_CONFIRMATION'
        else:
            return Response({"detail": "You cannot approve this request at its current stage."}, status=status.HTTP_400_BAD_REQUEST)

        req.status = new_status
        req.save()

        ApprovalLog.objects.create(
            function_request=req,
            approver=request.user,
            stage=role,
            status='APPROVED',
            remarks=remarks
        )

        if new_status == 'PENDING_FINAL_CONFIRMATION':
            from .notifications import send_management_confirmation_notification
            send_management_confirmation_notification(req)
        elif new_status == 'PENDING_DEAN':
            from .notifications import send_dean_notification
            send_dean_notification(req)
        elif new_status == 'PENDING_MANAGEMENT':
            from .notifications import send_management_notification
            send_management_notification(req)
        elif new_status == 'PENDING_PRINCIPAL':
            from .notifications import send_principal_notification
            send_principal_notification(req)

        return Response({"status": "approved", "new_status": new_status})

    @action(detail=True, methods=['post'])
    def confirm_booking(self, request, pk=None):
        req = self.get_object()
        user = request.user
        remarks = request.data.get('remarks', 'Booking confirmed by Management')

        # Only Management/AO role is allowed to perform this action.
        if user.role != 'MANAGEMENT' and not user.is_superuser:
            return Response({"detail": "Only Management is authorized to confirm bookings."}, status=status.HTTP_403_FORBIDDEN)

        # Valid transition: PENDING_FINAL_CONFIRMATION -> APPROVED
        if req.status != 'PENDING_FINAL_CONFIRMATION':
            return Response({"detail": "Request must be in Pending Final Confirmation stage to confirm booking."}, status=status.HTTP_400_BAD_REQUEST)

        # Double-booking check
        if check_double_booking(req.venue, req.start_date, req.end_date, req.time_from, req.time_to, exclude_req_id=req.id):
            return Response({"detail": "This seminar hall is already booked for the selected date and time range."}, status=status.HTTP_400_BAD_REQUEST)

        req.status = 'APPROVED'
        req.save()

        # Log transition to timeline
        ApprovalLog.objects.create(
            function_request=req,
            approver=user,
            stage='MANAGEMENT',
            status='APPROVED',
            remarks=remarks
        )

        from .notifications import send_faculty_confirmed_notification
        send_faculty_confirmed_notification(req)

        return Response({"status": "confirmed", "new_status": "APPROVED"})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        req = self.get_object()
        role = request.user.role
        remarks = request.data.get('remarks', '')

        if role not in ['HOD', 'DEAN_COMPUTING', 'MANAGEMENT', 'PRINCIPAL'] and not request.user.is_superuser:
            return Response({"detail": "Not authorized to reject requests."}, status=status.HTTP_403_FORBIDDEN)

        # HOD/Dean department checks
        if role == 'HOD':
            perm = IsHODDepartment()
        elif role == 'DEAN_COMPUTING':
            perm = IsDeanComputing()
        elif role == 'MANAGEMENT':
            perm = IsManagementAO()
        elif role == 'PRINCIPAL':
            perm = IsPrincipal()
            
        if role in ['HOD', 'DEAN_COMPUTING'] and not perm.has_object_permission(request, self, req):
            return Response({"detail": "Permission denied for this request context."}, status=status.HTTP_403_FORBIDDEN)

        req.status = 'REJECTED'
        req.save()

        ApprovalLog.objects.create(
            function_request=req,
            approver=request.user,
            stage=role,
            status='REJECTED',
            remarks=remarks
        )

        from .notifications import send_faculty_rejection_notification
        send_faculty_rejection_notification(req, remarks)

        return Response({"status": "rejected", "new_status": "REJECTED"})

    @action(detail=True, methods=['post'])
    def return_for_correction(self, request, pk=None):
        req = self.get_object()
        role = request.user.role
        remarks = request.data.get('remarks', '')

        if role not in ['HOD', 'DEAN_COMPUTING', 'MANAGEMENT', 'PRINCIPAL'] and not request.user.is_superuser:
            return Response({"detail": "Not authorized to return requests for correction."}, status=status.HTTP_403_FORBIDDEN)

        # Checks HOD/Dean department boundaries
        if role == 'HOD':
            perm = IsHODDepartment()
        elif role == 'DEAN_COMPUTING':
            perm = IsDeanComputing()
        elif role == 'MANAGEMENT':
            perm = IsManagementAO()
        elif role == 'PRINCIPAL':
            perm = IsPrincipal()
            
        if role in ['HOD', 'DEAN_COMPUTING'] and not perm.has_object_permission(request, self, req):
            return Response({"detail": "Permission denied for this request context."}, status=status.HTTP_403_FORBIDDEN)

        # Store previous status to resume from on resubmit
        req.previous_status = req.status
        req.status = 'RETURNED_FOR_CORRECTION'
        req.save()

        ApprovalLog.objects.create(
            function_request=req,
            approver=request.user,
            stage=role,
            status='RETURNED_FOR_CORRECTION',
            remarks=remarks
        )

        from .notifications import send_faculty_correction_notification
        send_faculty_correction_notification(req, remarks)

        return Response({"status": "returned_for_correction", "new_status": "RETURNED_FOR_CORRECTION"})

    @action(detail=True, methods=['post'])
    def cancel_request(self, request, pk=None):
        req = self.get_object()
        role = request.user.role
        remarks = request.data.get('remarks', 'Cancelled due to emergency')

        if role not in ['MANAGEMENT', 'PRINCIPAL'] and not request.user.is_superuser:
            return Response({"detail": "Not authorized to cancel requests."}, status=status.HTTP_403_FORBIDDEN)

        req.status = 'CANCELLED'
        req.save()

        ApprovalLog.objects.create(
            function_request=req,
            approver=request.user,
            stage=role,
            status='CANCELLED',
            remarks=remarks
        )

        from .notifications import send_cancellation_notification
        send_cancellation_notification(req, remarks)

        return Response({"status": "cancelled", "new_status": "CANCELLED"})

    @action(detail=True, methods=['get'])
    def generate_pdf(self, request, pk=None):
        from django.http import HttpResponse
        from .pdf_generator import generate_function_request_pdf
        
        req = self.get_object()
        pdf_buffer = generate_function_request_pdf(req)
        
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="function_request_{req.id}.pdf"'
        return response
