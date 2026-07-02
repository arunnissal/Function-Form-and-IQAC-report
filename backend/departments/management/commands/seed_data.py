from django.core.management.base import BaseCommand
from accounts.models import User
from departments.models import Department, HOD, Faculty
from halls.models import SeminarHall

class Command(BaseCommand):
    help = 'Seed database with dummy departments, users, and halls'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # Create Principal
        principal, _ = User.objects.get_or_create(username='principal', defaults={'role': 'PRINCIPAL', 'first_name': 'Dr. Principal'})
        principal.set_password('password123')
        principal.save()

        # Create Management
        management, _ = User.objects.get_or_create(username='management', defaults={'role': 'MANAGEMENT', 'first_name': 'AO Officer'})
        management.set_password('password123')
        management.save()
        
        # Create System Admin
        admin, _ = User.objects.get_or_create(username='admin', defaults={'role': 'ADMIN', 'first_name': 'System Admin', 'is_superuser': True, 'is_staff': True})
        admin.set_password('password123')
        admin.save()

        # Seminar Halls
        halls = [
            {'hall_name': 'Main Auditorium', 'capacity': 500, 'location': 'A Block', 'facilities': 'AC, Projector, Mic'},
            {'hall_name': 'Mini Hall 1', 'capacity': 100, 'location': 'B Block', 'facilities': 'AC, Projector'},
            {'hall_name': 'Conference Room', 'capacity': 50, 'location': 'Admin Block', 'facilities': 'AC, Projector, Mic'},
        ]
        for h in halls:
            SeminarHall.objects.get_or_create(hall_name=h['hall_name'], defaults=h)

        # Departments
        depts = [
            {'name': 'Computer Science', 'code': 'CSE'},
            {'name': 'Electronics', 'code': 'ECE'},
            {'name': 'Information Technology', 'code': 'IT'},
        ]

        for idx, d in enumerate(depts):
            dept, _ = Department.objects.get_or_create(department_code=d['code'], defaults={'department_name': d['name']})
            
            # HOD
            hod_user, _ = User.objects.get_or_create(username=f"hod_{d['code'].lower()}", defaults={'role': 'HOD', 'first_name': f"HOD {d['code']}"})
            hod_user.set_password('password123')
            hod_user.save()
            HOD.objects.get_or_create(user=hod_user, defaults={'department': dept})

            # Faculty
            for i in range(1, 4):
                fac_user, _ = User.objects.get_or_create(username=f"fac{i}_{d['code'].lower()}", defaults={'role': 'FACULTY', 'first_name': f"Faculty {i} {d['code']}"})
                fac_user.set_password('password123')
                fac_user.save()
                Faculty.objects.get_or_create(user=fac_user, defaults={'department': dept, 'designation': 'Assistant Professor', 'contact_number': '1234567890'})

        self.stdout.write(self.style.SUCCESS('Successfully seeded data'))
