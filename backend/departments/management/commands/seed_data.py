from django.core.management.base import BaseCommand
from accounts.models import User
from departments.models import Department, HOD, Faculty
from halls.models import SeminarHall

class Command(BaseCommand):
    help = 'Seed database with dummy departments, users, and halls'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # Create Principal
        principal, _ = User.objects.get_or_create(username='principal@drngpit.ac.in', defaults={'email': 'principal@drngpit.ac.in', 'role': 'PRINCIPAL', 'first_name': 'Dr. Principal'})
        principal.set_password('password123')
        principal.save()

        # Create Management
        management, _ = User.objects.get_or_create(username='ao@drngpit.ac.in', defaults={'email': 'ao@drngpit.ac.in', 'role': 'MANAGEMENT', 'first_name': 'AO Officer'})
        management.set_password('password123')
        management.save()
        
        # Create System Admin
        admin, _ = User.objects.get_or_create(username='admin@drngpit.ac.in', defaults={'email': 'admin@drngpit.ac.in', 'role': 'MANAGEMENT', 'first_name': 'System Admin', 'is_superuser': True, 'is_staff': True})
        admin.set_password('password123')
        admin.save()

        # Create standard admin username for Django admin panel compatibility
        admin_django, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@drngpit.ac.in', 'role': 'MANAGEMENT', 'first_name': 'System Admin', 'is_superuser': True, 'is_staff': True})
        admin_django.set_password('password123')
        admin_django.save()

        # Create Dean of Computing
        dean, _ = User.objects.get_or_create(username='dean@drngpit.ac.in', defaults={'email': 'dean@drngpit.ac.in', 'role': 'DEAN_COMPUTING', 'first_name': 'Dean of Computing'})
        dean.set_password('password123')
        dean.save()

        # Clean database to remove others and prevent duplicate conflicts
        from requests.models import FunctionRequest
        from approvals.models import ApprovalLog
        from resources.models import GuestHouseRequirement, RefreshmentRequirement, TransportRequirement, PowerCameraRequirement, MementoRequirement
        
        ApprovalLog.objects.all().delete()
        GuestHouseRequirement.objects.all().delete()
        RefreshmentRequirement.objects.all().delete()
        TransportRequirement.objects.all().delete()
        PowerCameraRequirement.objects.all().delete()
        MementoRequirement.objects.all().delete()
        FunctionRequest.objects.all().delete()

        User.objects.exclude(username__in=['admin', 'principal', 'management', 'ao@drngpit.ac.in', 'principal@drngpit.ac.in']).delete()
        Department.objects.all().delete()
        HOD.objects.all().delete()
        Faculty.objects.all().delete()
        SeminarHall.objects.all().delete()

        # Seminar Halls
        halls = [
            {'hall_name': 'Main Auditorium', 'capacity': 500, 'location': 'A Block', 'facilities': 'AC, Projector, Mic'},
            {'hall_name': 'Mini Hall 1', 'capacity': 100, 'location': 'B Block', 'facilities': 'AC, Projector'},
            {'hall_name': 'Conference Room', 'capacity': 50, 'location': 'Admin Block', 'facilities': 'AC, Projector, Mic'},
        ]
        for h in halls:
            SeminarHall.objects.get_or_create(hall_name=h['hall_name'], defaults=h)

        # Departments from the photo
        depts = [
            {'name': 'Artificial Intelligence & Data Science', 'code': 'AIDS'},
            {'name': 'Computer Science and Business Systems', 'code': 'CSBS'},
            {'name': 'Biomedical Engineering', 'code': 'BME'},
            {'name': 'Civil Engineering', 'code': 'CIVIL'},
            {'name': 'Computer Science and Engineering', 'code': 'CSE'},
            {'name': 'Electrical and Electronics Engineering', 'code': 'EEE'},
            {'name': 'Electronics and Communication Engineering', 'code': 'ECE'},
            {'name': 'Mechanical Engineering', 'code': 'MECH'},
            {'name': 'Information Technology', 'code': 'IT'},
            {'name': 'Computer Science and Engineering (Cyber Security)', 'code': 'CSE(CS)'},
        ]

        for idx, d in enumerate(depts):
            dept, _ = Department.objects.get_or_create(department_code=d['code'], defaults={'department_name': d['name']})
            clean_code = d['code'].lower().replace('(', '_').replace(')', '').replace('-', '_')
            
            # HOD
            hod_user, _ = User.objects.get_or_create(username=f"hod_{clean_code}@drngpit.ac.in", defaults={'email': f"hod_{clean_code}@drngpit.ac.in", 'role': 'HOD', 'first_name': f"HOD {d['code']}"})
            hod_user.set_password('password123')
            hod_user.save()
            HOD.objects.get_or_create(user=hod_user, defaults={'department': dept})

            # Faculty
            for i in range(1, 4):
                fac_user, _ = User.objects.get_or_create(username=f"fac{i}_{clean_code}@drngpit.ac.in", defaults={'email': f"fac{i}_{clean_code}@drngpit.ac.in", 'role': 'FACULTY', 'first_name': f"Faculty {i} {d['code']}"})
                fac_user.set_password('password123')
                fac_user.save()
                Faculty.objects.get_or_create(user=fac_user, defaults={'department': dept, 'designation': 'Assistant Professor', 'contact_number': '1234567890'})

        self.stdout.write(self.style.SUCCESS('Successfully seeded data'))
