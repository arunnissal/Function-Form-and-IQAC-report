from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from departments.models import Department, HOD, Faculty
from requests.models import FunctionRequest
from approvals.models import ApprovalLog
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class ApprovalsWorkflowTestCase(TestCase):
    def setUp(self):
        # Create departments
        self.cse_dept = Department.objects.create(department_code='CSE', department_name='Computer Science')
        self.eee_dept = Department.objects.create(department_code='EEE', department_name='Electrical Engineering')

        # Create users
        self.principal_user = User.objects.create_user(username='principal@drngpit.ac.in', password='password123', role='PRINCIPAL')
        self.management_user = User.objects.create_user(username='ao@drngpit.ac.in', password='password123', role='MANAGEMENT')
        self.dean_user = User.objects.create_user(username='dean@drngpit.ac.in', password='password123', role='DEAN_COMPUTING')

        self.hod_cse_user = User.objects.create_user(username='hod_cse@drngpit.ac.in', password='password123', role='HOD')
        HOD.objects.create(user=self.hod_cse_user, department=self.cse_dept)

        self.hod_eee_user = User.objects.create_user(username='hod_eee@drngpit.ac.in', password='password123', role='HOD')
        HOD.objects.create(user=self.hod_eee_user, department=self.eee_dept)

        self.fac_cse_user = User.objects.create_user(username='fac_cse@drngpit.ac.in', password='password123', role='FACULTY')
        self.fac_cse = Faculty.objects.create(user=self.fac_cse_user, department=self.cse_dept, designation='Assistant Professor')

        self.fac_eee_user = User.objects.create_user(username='fac_eee@drngpit.ac.in', password='password123', role='FACULTY')
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

        # 5. Principal Approves -> APPROVED
        url = f"/api/v1/requests/{request.id}/approve/"
        response = self.client.post(
            url, data={}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.principal_token}"
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

        # 4. Principal Approves -> APPROVED
        url = f"/api/v1/requests/{request.id}/approve/"
        response = self.client.post(
            url, data={}, content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.principal_token}"
        )
        self.assertEqual(response.status_code, 200)
        request.refresh_from_db()
        self.assertEqual(request.status, 'APPROVED')
