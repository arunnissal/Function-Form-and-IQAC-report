from django.core.management.base import BaseCommand
from accounts.models import User
from departments.models import Department, HOD
from halls.models import SeminarHall

class Command(BaseCommand):
    help = 'Seeds the database with default departments, halls, and users (HODs, Management, Principal)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting database seeding...')

        # 1. Create Departments
        departments_data = [
            {'department_name': 'Computer Science and Engineering', 'department_code': 'CSE'},
            {'department_name': 'Electronics and Communication Engineering', 'department_code': 'ECE'},
            {'department_name': 'Information Technology', 'department_code': 'IT'},
            {'department_name': 'Mechanical Engineering', 'department_code': 'MECH'},
            {'department_name': 'Civil Engineering', 'department_code': 'CIVIL'},
        ]

        departments = {}
        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                department_code=dept_data['department_code'],
                defaults={'department_name': dept_data['department_name']}
            )
            departments[dept_data['department_code']] = dept
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Department: {dept.department_code}"))

        # 2. Create Seminar Halls
        halls_data = [
            {'hall_name': 'Main Auditorium', 'capacity': 1000},
            {'hall_name': 'CSE Seminar Hall', 'capacity': 150},
            {'hall_name': 'IT Seminar Hall', 'capacity': 120},
            {'hall_name': 'ECE Seminar Hall', 'capacity': 200},
        ]

        for hall_data in halls_data:
            hall, created = SeminarHall.objects.get_or_create(
                hall_name=hall_data['hall_name'],
                defaults={'capacity': hall_data['capacity']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Seminar Hall: {hall.hall_name}"))

        # 3. Create Default Users (Principal, Management)
        users_to_create = [
            {'email': 'principal@drngpit.ac.in', 'name': 'Principal', 'role': 'PRINCIPAL'},
            {'email': 'management@drngpit.ac.in', 'name': 'Management', 'role': 'MANAGEMENT'},
        ]

        for u in users_to_create:
            user, created = User.objects.get_or_create(username=u['email'], defaults={
                'email': u['email'],
                'first_name': u['name'],
                'role': u['role'],
                'is_staff': True
            })
            if created:
                user.set_password('Admin@123')
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created {u['role']} User: {user.email} (Password: Admin@123)"))

        # 4. Create HODs for Departments
        for code, dept in departments.items():
            email = f"hod_{code.lower()}@drngpit.ac.in"
            user, created = User.objects.get_or_create(username=email, defaults={
                'email': email,
                'first_name': f"HOD {code}",
                'role': 'HOD',
                'is_staff': True
            })
            if created:
                user.set_password('Hod@123')
                user.save()
            
            HOD.objects.get_or_create(user=user, defaults={'department': dept})
            
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created HOD for {code}: {user.email} (Password: Hod@123)"))

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
