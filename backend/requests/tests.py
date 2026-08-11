from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from departments.models import Department, HOD, Faculty
from requests.models import FunctionRequest
from approvals.models import ApprovalLog
from rest_framework_simplejwt.tokens import RefreshToken
from halls.models import SeminarHall

User = get_user_model()

class ApprovalsWorkflowTestCase(TestCase):
    def setUp(self):
        # Create departments
        self.cse_dept = Department.objects.create(department_code='CSE', department_name='Computer Science')
        self.eee_dept = Department.objects.create(department_code='EEE', department_name='Electrical Engineering')

        # Create users
        self.principal_user = User.objects.create_user(username='principal@drngpit.ac.in', password='password123', role='PRINCIPAL', email='principal@drngpit.ac.in')
        self.management_user = User.objects.create_user(username='ao@drngpit.ac.in', password='password123', role='MANAGEMENT', email='ao@drngpit.ac.in')
        self.dean_user = User.objects.create_user(username='dean@drngpit.ac.in', password='password123', role='DEAN_COMPUTING', email='dean@drngpit.ac.in')

        self.hod_cse_user = User.objects.create_user(username='hod_cse@drngpit.ac.in', password='password123', role='HOD', email='hod_cse@drngpit.ac.in')
        HOD.objects.create(user=self.hod_cse_user, department=self.cse_dept)

        self.hod_eee_user = User.objects.create_user(username='hod_eee@drngpit.ac.in', password='password123', role='HOD', email='hod_eee@drngpit.ac.in')
        HOD.objects.create(user=self.hod_eee_user, department=self.eee_dept)

        self.fac_cse_user = User.objects.create_user(username='fac_cse@drngpit.ac.in', password='password123', role='FACULTY', email='fac_cse@drngpit.ac.in')
        self.fac_cse = Faculty.objects.create(user=self.fac_cse_user, department=self.cse_dept, designation='Assistant Professor')

        self.fac_eee_user = User.objects.create_user(username='fac_eee@drngpit.ac.in', password='password123', role='FACULTY', email='fac_eee@drngpit.ac.in')
        self.fac_eee = Faculty.objects.create(user=self.fac_eee_user, department=self.eee_dept, designation='Assistant Professor')

        # Generate JWT Tokens
        self.hod_cse_token = str(RefreshToken.for_user(self.hod_cse_user).access_token)
        self.hod_eee_token = str(RefreshToken.for_user(self.hod_eee_user).access_token)
        self.dean_token = str(RefreshToken.for_user(self.dean_user).access_token)
        self.management_token = str(RefreshToken.for_user(self.management_user).access_token)
        self.principal_token = str(RefreshToken.for_user(self.principal_user).access_token)

        # Setup Client
        self.client = Client()

    def test_computing_department_approval_flow(self):
        # 1. Faculty creates a request
        request = FunctionRequest.objects.create(
            faculty=self.fac_cse,
            department=self.cse_dept,
            function_name="CSE Tech Fest",
            function_type="Workshop",
            time_from="09:00:00",
            time_to="16:00:00",
            status="PENDING_HOD"
        )
        
        # 2. HOD Approves -> transitions to PENDING_DEAN (computing cluster)
        url = f"/api/v1/requests/{request.id}/approve/"
        response = self.client.post(
            url, data={}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.hod_cse_token}"
        )
        self.assertEqual(response.status_code, 200)
        request.refresh_from_db()
        self.assertEqual(request.status, 'PENDING_DEAN')

        # 3. Dean of Computing Approves -> transitions to PENDING_MANAGEMENT
        url = f"/api/v1/requests/{request.id}/approve/"
        response = self.client.post(
            url, data={}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.dean_token}"
        )
        self.assertEqual(response.status_code, 200)
        request.refresh_from_db()
        self.assertEqual(request.status, 'PENDING_MANAGEMENT')

        # 4. Management Approves -> PENDING_PRINCIPAL
        url = f"/api/v1/requests/{request.id}/approve/"
        response = self.client.post(
            url, data={}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.management_token}"
        )
        self.assertEqual(response.status_code, 200)
        request.refresh_from_db()
        self.assertEqual(request.status, 'PENDING_PRINCIPAL')

        # 5. Principal Approves -> PENDING_FINAL_CONFIRMATION
        url = f"/api/v1/requests/{request.id}/approve/"
        response = self.client.post(
            url, data={}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.principal_token}"
        )
        self.assertEqual(response.status_code, 200)
        request.refresh_from_db()
        self.assertEqual(request.status, 'PENDING_FINAL_CONFIRMATION')

        # 6. Management Confirms Booking -> APPROVED
        url = f"/api/v1/requests/{request.id}/confirm_booking/"
        response = self.client.post(
            url, data={"remarks": "Final confirmation by AO"}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.management_token}"
        )
        self.assertEqual(response.status_code, 200)
        request.refresh_from_db()
        self.assertEqual(request.status, 'APPROVED')

    def test_non_computing_department_approval_flow(self):
        # 1. Faculty creates a request
        request = FunctionRequest.objects.create(
            faculty=self.fac_eee,
            department=self.eee_dept,
            function_name="EEE Symposium",
            function_type="Symposium",
            time_from="09:00:00",
            time_to="16:00:00",
            status="PENDING_HOD"
        )
        
        # 2. HOD Approves -> transitions directly to PENDING_MANAGEMENT (non-computing cluster)
        url = f"/api/v1/requests/{request.id}/approve/"
        response = self.client.post(
            url, data={}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.hod_eee_token}"
        )
        self.assertEqual(response.status_code, 200)
        request.refresh_from_db()
        self.assertEqual(request.status, 'PENDING_MANAGEMENT')

        # 3. Management Approves -> PENDING_PRINCIPAL
        url = f"/api/v1/requests/{request.id}/approve/"
        response = self.client.post(
            url, data={}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.management_token}"
        )
        self.assertEqual(response.status_code, 200)
        request.refresh_from_db()
        self.assertEqual(request.status, 'PENDING_PRINCIPAL')

        # 4. Principal Approves -> PENDING_FINAL_CONFIRMATION
        url = f"/api/v1/requests/{request.id}/approve/"
        response = self.client.post(
            url, data={}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.principal_token}"
        )
        self.assertEqual(response.status_code, 200)
        request.refresh_from_db()
        self.assertEqual(request.status, 'PENDING_FINAL_CONFIRMATION')

        # 5. Management Confirms Booking -> APPROVED
        url = f"/api/v1/requests/{request.id}/confirm_booking/"
        response = self.client.post(
            url, data={"remarks": "Final confirmation by AO"}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.management_token}"
        )
        self.assertEqual(response.status_code, 200)
        request.refresh_from_db()
        self.assertEqual(request.status, 'APPROVED')

    def test_return_for_correction_and_resubmit(self):
        # 1. Create request
        request = FunctionRequest.objects.create(
            faculty=self.fac_cse,
            department=self.cse_dept,
            function_name="CSE Session",
            function_type="Workshop",
            time_from="09:00:00",
            time_to="12:00:00",
            status="PENDING_HOD"
        )
        
        # 2. HOD returns for correction
        url = f"/api/v1/requests/{request.id}/return_for_correction/"
        response = self.client.post(
            url, data={"remarks": "Please change time"}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.hod_cse_token}"
        )
        self.assertEqual(response.status_code, 200)
        request.refresh_from_db()
        self.assertEqual(request.status, 'RETURNED_FOR_CORRECTION')
        self.assertEqual(request.previous_status, 'PENDING_HOD')
        
        # 3. Faculty edits and resubmits
        # We need to simulate Faculty authentication token
        fac_token = str(RefreshToken.for_user(self.fac_cse_user).access_token)
        url = f"/api/v1/requests/{request.id}/"
        response = self.client.put(
            url, data={"function_name": "CSE Session Updated", "resubmit": True}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {fac_token}"
        )
        self.assertEqual(response.status_code, 200)
        request.refresh_from_db()
        self.assertEqual(request.status, 'PENDING_HOD')

    def test_double_booking_prevention(self):
        # 1. Create first request and approve it fully
        hall = SeminarHall.objects.create(hall_name="Main Auditorium", capacity=500, location="Block A")
        request1 = FunctionRequest.objects.create(
            faculty=self.fac_cse,
            department=self.cse_dept,
            venue=hall,
            function_name="Approved Event",
            function_type="Symposium",
            start_date="2026-09-10",
            end_date="2026-09-10",
            time_from="09:00:00",
            time_to="13:00:00",
            status="PENDING_PRINCIPAL"
        )
        # Principal approves it
        self.client.post(
            f"/api/v1/requests/{request1.id}/approve/", data={}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.principal_token}"
        )
        # Management confirms booking
        self.client.post(
            f"/api/v1/requests/{request1.id}/confirm_booking/", data={}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.management_token}"
        )
        request1.refresh_from_db()
        self.assertEqual(request1.status, 'APPROVED')
        
        # 2. Create second overlapping request
        request2 = FunctionRequest.objects.create(
            faculty=self.fac_eee,
            department=self.eee_dept,
            venue=hall,
            function_name="Overlapping Event",
            function_type="Symposium",
            start_date="2026-09-10",
            end_date="2026-09-10",
            time_from="11:00:00",
            time_to="15:00:00",
            status="PENDING_MANAGEMENT"
        )
        
        # 3. Management tries to approve but should be blocked due to overlap
        response = self.client.post(
            f"/api/v1/requests/{request2.id}/approve/", data={}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.management_token}"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("already booked", response.json().get("detail", ""))

    def test_returned_from_final_confirmation_and_resubmit(self):
        # 1. Create request in PENDING_FINAL_CONFIRMATION stage
        request = FunctionRequest.objects.create(
            faculty=self.fac_cse,
            department=self.cse_dept,
            function_name="CSE Final Confirmation",
            function_type="Seminar",
            time_from="09:00:00",
            time_to="12:00:00",
            status="PENDING_FINAL_CONFIRMATION"
        )
        
        # 2. Management returns it for correction
        url = f"/api/v1/requests/{request.id}/return_for_correction/"
        response = self.client.post(
            url, data={"remarks": "Need to clarify guest details"}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.management_token}"
        )
        self.assertEqual(response.status_code, 200)
        request.refresh_from_db()
        self.assertEqual(request.status, 'RETURNED_FOR_CORRECTION')
        self.assertEqual(request.previous_status, 'PENDING_FINAL_CONFIRMATION')
        
        # 3. Faculty resubmits request
        fac_token = str(RefreshToken.for_user(self.fac_cse_user).access_token)
        url = f"/api/v1/requests/{request.id}/"
        response = self.client.put(
            url, data={"function_name": "CSE Final Confirmation Updated", "resubmit": True}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {fac_token}"
        )
        self.assertEqual(response.status_code, 200)
        request.refresh_from_db()
        self.assertEqual(request.status, 'PENDING_FINAL_CONFIRMATION')

    def test_confirm_booking_permissions(self):
        # 1. Create request in PENDING_FINAL_CONFIRMATION stage
        request = FunctionRequest.objects.create(
            faculty=self.fac_cse,
            department=self.cse_dept,
            function_name="Permission Check Event",
            function_type="Workshop",
            time_from="09:00:00",
            time_to="12:00:00",
            status="PENDING_FINAL_CONFIRMATION"
        )
        
        # Try confirming with unauthorized roles (Faculty, HOD, Dean, Principal)
        unauthorized_tokens = [
            str(RefreshToken.for_user(self.fac_cse_user).access_token),
            self.hod_cse_token,
            self.dean_token,
            self.principal_token
        ]
        
        for token in unauthorized_tokens:
            response = self.client.post(
                f"/api/v1/requests/{request.id}/confirm_booking/", data={}, content_type='application/json',
                HTTP_AUTHORIZATION=f"Bearer {token}"
            )
            self.assertEqual(response.status_code, 403)
            
        # Confirm with authorized Management/AO role
        response = self.client.post(
            f"/api/v1/requests/{request.id}/confirm_booking/", data={"remarks": "Verified by Management"}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.management_token}"
        )
        self.assertEqual(response.status_code, 200)
        request.refresh_from_db()
        self.assertEqual(request.status, 'APPROVED')

    def test_invalid_transition_confirm_booking(self):
        # Create request in non PENDING_FINAL_CONFIRMATION stage
        request = FunctionRequest.objects.create(
            faculty=self.fac_cse,
            department=self.cse_dept,
            function_name="Invalid Stage Confirm",
            function_type="Seminar",
            time_from="09:00:00",
            time_to="12:00:00",
            status="PENDING_HOD"
        )
        # Management tries to confirm booking
        response = self.client.post(
            f"/api/v1/requests/{request.id}/confirm_booking/", data={}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.management_token}"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Pending Final Confirmation stage", response.json().get("detail", ""))

    def test_double_booking_prevention_at_final_confirmation(self):
        hall = SeminarHall.objects.create(hall_name="Main Hall", capacity=200, location="Block B")
        # 1. Create and confirm first request
        request1 = FunctionRequest.objects.create(
            faculty=self.fac_cse,
            department=self.cse_dept,
            venue=hall,
            function_name="Confirmed Event 1",
            function_type="Symposium",
            start_date="2026-10-10",
            end_date="2026-10-10",
            time_from="09:00:00",
            time_to="12:00:00",
            status="APPROVED"
        )
        
        # 2. Create second overlapping request in PENDING_FINAL_CONFIRMATION stage
        request2 = FunctionRequest.objects.create(
            faculty=self.fac_eee,
            department=self.eee_dept,
            venue=hall,
            function_name="Overlapping Event 2",
            function_type="Workshop",
            start_date="2026-10-10",
            end_date="2026-10-10",
            time_from="10:00:00",
            time_to="14:00:00",
            status="PENDING_FINAL_CONFIRMATION"
        )
        
        # 3. Management tries to confirm request2 but should be blocked due to overlap with request1
        response = self.client.post(
            f"/api/v1/requests/{request2.id}/confirm_booking/", data={}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.management_token}"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("already booked", response.json().get("detail", ""))
        request2.refresh_from_db()
        self.assertEqual(request2.status, 'PENDING_FINAL_CONFIRMATION')

    def test_cancellation_and_release_at_final_confirmation(self):
        hall = SeminarHall.objects.create(hall_name="Main Hall", capacity=200, location="Block B")
        request = FunctionRequest.objects.create(
            faculty=self.fac_cse,
            department=self.cse_dept,
            venue=hall,
            function_name="Event to Cancel",
            function_type="Workshop",
            start_date="2026-10-10",
            end_date="2026-10-10",
            time_from="09:00:00",
            time_to="12:00:00",
            status="PENDING_FINAL_CONFIRMATION"
        )
        
        # Cancel the request from final confirmation
        response = self.client.post(
            f"/api/v1/requests/{request.id}/cancel_request/", data={"remarks": "AO Cancelled"}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.management_token}"
        )
        self.assertEqual(response.status_code, 200)
        request.refresh_from_db()
        self.assertEqual(request.status, 'CANCELLED')

    def test_audit_trail_for_new_workflow(self):
        request = FunctionRequest.objects.create(
            faculty=self.fac_cse,
            department=self.cse_dept,
            function_name="Audit Trail Event",
            function_type="Workshop",
            time_from="09:00:00",
            time_to="12:00:00",
            status="PENDING_PRINCIPAL"
        )
        
        # 1. Principal Approves -> PENDING_FINAL_CONFIRMATION
        self.client.post(
            f"/api/v1/requests/{request.id}/approve/", data={"remarks": "Principal Checked"}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.principal_token}"
        )
        
        # 2. Management Confirms Booking -> APPROVED
        self.client.post(
            f"/api/v1/requests/{request.id}/confirm_booking/", data={"remarks": "AO Confirmed"}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.management_token}"
        )
        
        # Verify logs
        logs = ApprovalLog.objects.filter(function_request=request).order_by('timestamp')
        self.assertEqual(logs.count(), 2)
        
        # Check Principal log
        principal_log = logs[0]
        self.assertEqual(principal_log.stage, 'PRINCIPAL')
        self.assertEqual(principal_log.status, 'APPROVED') # Principal action is approve
        self.assertEqual(principal_log.remarks, 'Principal Checked')
        
        # Check Management log
        management_log = logs[1]
        self.assertEqual(management_log.stage, 'MANAGEMENT')
        self.assertEqual(management_log.status, 'APPROVED')
        self.assertEqual(management_log.remarks, 'AO Confirmed')

    def test_faculty_submission_notifies_hod(self):
        from django.core import mail
        mail.outbox = []

        fac_token = str(RefreshToken.for_user(self.fac_cse_user).access_token)
        url = "/api/v1/requests/"
        payload = {
            "function_name": "Faculty Submit Test",
            "function_type": "Workshop",
            "start_date": "2026-09-15",
            "end_date": "2026-09-15",
            "time_from": "09:00:00",
            "time_to": "12:00:00",
            "number_of_students": 50,
            "status": "PENDING_HOD",
            "organizer_name": "Dr. CSE Faculty",
            "organizer_contact": "9876543210",
            "guest_house": {"required": False, "room_type": "AC", "guest_count": 0, "check_in_date": None, "check_out_date": None},
            "refreshment": {"tea_required": False, "coffee_required": False, "tea_count": 0, "coffee_count": 0, "breakfast_required": False, "breakfast_count": 0, "lunch_required": False, "lunch_count": 0, "vip_count": 0, "staff_count": 0, "student_count": 0, "payment_by_association": False},
            "transport": {"required": False, "pickup_location": "", "pickup_time": None, "drop_location": "", "drop_time": None, "guest_contact": ""},
            "power_camera": {"mic_required": False, "cordless_mics": 0, "collar_mics": 0, "ac_required": False, "projector_required": False, "laptop_required": False, "system_technician_required": False, "power_backup_required": False, "photography_required": False, "videography_required": False, "technician_names": "", "remarks": ""},
            "memento": {"required": False, "quantity": 0, "honorarium_worth": 0, "dias_seats": 0, "audience_seats": 0, "table_cloths": 0, "welcome_banner_required": False, "background_screen_text": "", "reception_items": ""}
        }
        
        response = self.client.post(
            url, data=payload, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {fac_token}"
        )
        self.assertEqual(response.status_code, 201)
        created_id = response.json().get('id')
        
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ['hod_cse@drngpit.ac.in'])
        self.assertIn("Faculty Submit Test", email.body)
        self.assertIn(f"Request ID: #{created_id}", email.body)
        self.assertIn("Pending HOD Approval", email.body)

    def test_principal_approval_notifies_management(self):
        from django.core import mail
        mail.outbox = []

        request = FunctionRequest.objects.create(
            faculty=self.fac_cse,
            department=self.cse_dept,
            function_name="Principal Notify Management Test",
            function_type="Workshop",
            time_from="09:00:00",
            time_to="12:00:00",
            status="PENDING_PRINCIPAL"
        )
        
        url = f"/api/v1/requests/{request.id}/approve/"
        response = self.client.post(
            url, data={"remarks": "Principal approves"}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.principal_token}"
        )
        self.assertEqual(response.status_code, 200)
        request.refresh_from_db()
        self.assertEqual(request.status, 'PENDING_FINAL_CONFIRMATION')
        
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ['ao@drngpit.ac.in'])
        self.assertIn("Principal Notify Management Test", email.body)
        self.assertIn(f"Request ID: #{request.id}", email.body)
        self.assertIn("Pending Final Confirmation", email.body)

    def test_email_failure_does_not_break_transaction(self):
        from unittest.mock import patch
        
        request = FunctionRequest.objects.create(
            faculty=self.fac_cse,
            department=self.cse_dept,
            function_name="Mock Failure Test",
            function_type="Workshop",
            time_from="09:00:00",
            time_to="12:00:00",
            status="PENDING_PRINCIPAL"
        )
        
        with patch('requests.notifications.send_mail', side_effect=Exception("SMTP Connection Error")):
            url = f"/api/v1/requests/{request.id}/approve/"
            response = self.client.post(
                url, data={"remarks": "Principal approves"}, content_type='application/json',
                HTTP_AUTHORIZATION=f"Bearer {self.principal_token}"
            )
            self.assertEqual(response.status_code, 200)
            request.refresh_from_db()
            self.assertEqual(request.status, 'PENDING_FINAL_CONFIRMATION')

    def test_hod_approval_notifies_next(self):
        from django.core import mail
        # Computing Department (CSE)
        request1 = FunctionRequest.objects.create(
            faculty=self.fac_cse,
            department=self.cse_dept,
            function_name="Computing Event",
            function_type="Workshop",
            time_from="09:00:00",
            time_to="12:00:00",
            status="PENDING_HOD"
        )
        mail.outbox = []
        self.client.post(
            f"/api/v1/requests/{request1.id}/approve/", data={"remarks": "HOD CSE approves"}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.hod_cse_token}"
        )
        # Should transition to PENDING_DEAN and notify Dean
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['dean@drngpit.ac.in'])
        self.assertIn("Pending Dean Approval", mail.outbox[0].body)

        # Non-computing Department (EEE)
        request2 = FunctionRequest.objects.create(
            faculty=self.fac_eee,
            department=self.eee_dept,
            function_name="Non-Computing Event",
            function_type="Workshop",
            time_from="09:00:00",
            time_to="12:00:00",
            status="PENDING_HOD"
        )
        mail.outbox = []
        self.client.post(
            f"/api/v1/requests/{request2.id}/approve/", data={"remarks": "HOD EEE approves"}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.hod_eee_token}"
        )
        # Should transition to PENDING_MANAGEMENT and notify Management
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['ao@drngpit.ac.in'])
        self.assertIn("Pending Management Approval", mail.outbox[0].body)

    def test_dean_approval_notifies_management(self):
        from django.core import mail
        request = FunctionRequest.objects.create(
            faculty=self.fac_cse,
            department=self.cse_dept,
            function_name="Dean Event",
            function_type="Workshop",
            time_from="09:00:00",
            time_to="12:00:00",
            status="PENDING_DEAN"
        )
        mail.outbox = []
        self.client.post(
            f"/api/v1/requests/{request.id}/approve/", data={"remarks": "Dean approves"}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.dean_token}"
        )
        # Should transition to PENDING_MANAGEMENT and notify Management
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['ao@drngpit.ac.in'])
        self.assertIn("Pending Management Approval", mail.outbox[0].body)

    def test_management_approval_notifies_principal(self):
        from django.core import mail
        hall = SeminarHall.objects.create(hall_name="Main Aud", capacity=300, location="Block A")
        request = FunctionRequest.objects.create(
            faculty=self.fac_cse,
            department=self.cse_dept,
            venue=hall,
            function_name="Mgmt Event",
            function_type="Workshop",
            time_from="09:00:00",
            time_to="12:00:00",
            status="PENDING_MANAGEMENT"
        )
        mail.outbox = []
        self.client.post(
            f"/api/v1/requests/{request.id}/approve/", data={"remarks": "AO approves"}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.management_token}"
        )
        # Should transition to PENDING_PRINCIPAL and notify Principal
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['principal@drngpit.ac.in'])
        self.assertIn("Pending Principal Approval", mail.outbox[0].body)

    def test_final_confirmation_notifies_faculty(self):
        from django.core import mail
        hall = SeminarHall.objects.create(hall_name="Main Aud", capacity=300, location="Block A")
        request = FunctionRequest.objects.create(
            faculty=self.fac_cse,
            department=self.cse_dept,
            venue=hall,
            function_name="Confirm Event",
            function_type="Workshop",
            time_from="09:00:00",
            time_to="12:00:00",
            status="PENDING_FINAL_CONFIRMATION"
        )
        mail.outbox = []
        self.client.post(
            f"/api/v1/requests/{request.id}/confirm_booking/", data={"remarks": "AO confirms"}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.management_token}"
        )
        # Should transition to APPROVED and notify Faculty
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['fac_cse@drngpit.ac.in'])
        self.assertIn("approved and confirmed", mail.outbox[0].body)

    def test_return_for_correction_notifies_faculty(self):
        from django.core import mail
        request = FunctionRequest.objects.create(
            faculty=self.fac_cse,
            department=self.cse_dept,
            function_name="Return Event",
            function_type="Workshop",
            time_from="09:00:00",
            time_to="12:00:00",
            status="PENDING_HOD"
        )
        mail.outbox = []
        self.client.post(
            f"/api/v1/requests/{request.id}/return_for_correction/", data={"remarks": "Missing details about speakers"}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.hod_cse_token}"
        )
        # Should notify Faculty and include remarks
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['fac_cse@drngpit.ac.in'])
        self.assertIn("RETURNED_FOR_CORRECTION", mail.outbox[0].body)
        self.assertIn("Missing details about speakers", mail.outbox[0].body)

    def test_rejection_notifies_faculty(self):
        from django.core import mail
        request = FunctionRequest.objects.create(
            faculty=self.fac_cse,
            department=self.cse_dept,
            function_name="Reject Event",
            function_type="Workshop",
            time_from="09:00:00",
            time_to="12:00:00",
            status="PENDING_HOD"
        )
        mail.outbox = []
        self.client.post(
            f"/api/v1/requests/{request.id}/reject/", data={"remarks": "Conflict of university exams"}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.hod_cse_token}"
        )
        # Should notify Faculty and include remarks
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['fac_cse@drngpit.ac.in'])
        self.assertIn("REJECTED", mail.outbox[0].body)
        self.assertIn("Conflict of university exams", mail.outbox[0].body)

    def test_resubmission_notifies_correct_reviewer(self):
        from django.core import mail
        request = FunctionRequest.objects.create(
            faculty=self.fac_cse,
            department=self.cse_dept,
            function_name="Resubmit Event",
            function_type="Workshop",
            time_from="09:00:00",
            time_to="12:00:00",
            status="RETURNED_FOR_CORRECTION",
            previous_status="PENDING_PRINCIPAL"
        )
        mail.outbox = []
        fac_token = str(RefreshToken.for_user(self.fac_cse_user).access_token)
        self.client.put(
            f"/api/v1/requests/{request.id}/", data={"function_name": "Resubmit Event Updated", "resubmit": True}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {fac_token}"
        )
        # Resubmission transitions back to previous_status (PENDING_PRINCIPAL) and notifies Principal
        request.refresh_from_db()
        self.assertEqual(request.status, 'PENDING_PRINCIPAL')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['principal@drngpit.ac.in'])
        self.assertIn("Pending Principal Approval", mail.outbox[0].body)

    def test_cancellation_notifies_stakeholders(self):
        from django.core import mail
        hall = SeminarHall.objects.create(hall_name="Main Aud", capacity=300, location="Block A")
        request = FunctionRequest.objects.create(
            faculty=self.fac_cse,
            department=self.cse_dept,
            venue=hall,
            function_name="Cancel Event",
            function_type="Workshop",
            time_from="09:00:00",
            time_to="12:00:00",
            status="APPROVED"
        )
        mail.outbox = []
        self.client.post(
            f"/api/v1/requests/{request.id}/cancel_request/", data={"remarks": "Emergency lockdown"}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.management_token}"
        )
        # Should transition to CANCELLED and notify Faculty, HOD, and Management
        request.refresh_from_db()
        self.assertEqual(request.status, 'CANCELLED')
        
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        # Should include Faculty, HOD, and Management recipients
        expected_recipients = {'fac_cse@drngpit.ac.in', 'hod_cse@drngpit.ac.in', 'ao@drngpit.ac.in'}
        self.assertEqual(set(email.to), expected_recipients)
        self.assertIn("CANCELLED", email.body)
        self.assertIn("Emergency lockdown", email.body)

    def test_pdf_generation_endpoints_and_safety(self):
        hall = SeminarHall.objects.create(hall_name="Main Hall", capacity=200, location="Block B")
        request = FunctionRequest.objects.create(
            faculty=self.fac_cse,
            department=self.cse_dept,
            venue=hall,
            function_name="PDF Form Gen Test Event",
            function_type="Symposium",
            start_date="2026-10-10",
            end_date="2026-10-10",
            time_from="09:00:00",
            time_to="12:00:00",
            status="PENDING_HOD",
            number_of_students=150,
            class_name="III CSE"
        )
        # Create resource requirements
        from resources.models import GuestHouseRequirement, RefreshmentRequirement
        GuestHouseRequirement.objects.create(function_request=request, required=True, number_of_persons=2)
        RefreshmentRequirement.objects.create(function_request=request, tea_required=True, coffee_required=False, tiffin_count=10)

        fac_token = str(RefreshToken.for_user(self.fac_cse_user).access_token)
        url = f"/api/v1/requests/{request.id}/generate_pdf/"
        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=f"Bearer {fac_token}"
        )
        
        # Verify response status and header content type
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/pdf')
        
        # Verify request status has NOT changed
        request.refresh_from_db()
        self.assertEqual(request.status, 'PENDING_HOD')
        
        # Verify valid PDF signature
        content = response.content
        self.assertTrue(content.startswith(b'%PDF'))
        self.assertGreater(len(content), 1000)

    def test_hod_can_update_request_academic_fields(self):
        request = FunctionRequest.objects.create(
            faculty=self.fac_cse,
            department=self.cse_dept,
            function_name="CSE Tech Fest",
            function_type="Workshop",
            time_from="09:00:00",
            time_to="16:00:00",
            status="PENDING_HOD",
            class_name="III CSE"
        )
        url = f"/api/v1/requests/{request.id}/"
        # HOD updates the class name (academic field)
        response = self.client.put(
            url,
            data={"class_name": "IV CSE"},
            content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.hod_cse_token}"
        )
        self.assertEqual(response.status_code, 200)
        request.refresh_from_db()
        self.assertEqual(request.class_name, "IV CSE")

    def test_management_can_update_logistics_but_blocked_on_academic(self):
        request = FunctionRequest.objects.create(
            faculty=self.fac_cse,
            department=self.cse_dept,
            function_name="CSE Tech Fest",
            function_type="Workshop",
            time_from="09:00:00",
            time_to="16:00:00",
            status="PENDING_MANAGEMENT"
        )
        url = f"/api/v1/requests/{request.id}/"
        # Management tries to update logistics
        response = self.client.put(
            url,
            data={"memento": {"required": True, "quantity": 3}},
            content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.management_token}"
        )
        self.assertEqual(response.status_code, 200)
        
        # Management tries to update function name (blocked academic field)
        response = self.client.put(
            url,
            data={"function_name": "Illegal Name Modification"},
            content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.management_token}"
        )
        self.assertEqual(response.status_code, 403)

