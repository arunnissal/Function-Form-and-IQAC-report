from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import get_user_model
import random
import string

User = get_user_model()

# Store OTPs in session or simple memory dict for prototype
# In production, use Cache or DB
OTP_STORE = {}

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        position = request.POST.get('position')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email.endswith('@drngpit.ac.in'):
            messages.error(request, "Mail id must end with @drngpit.ac.in")
            return render(request, 'registration/login.html')

        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            # Map position to internal roles
            # position from UI could be "AO", "Staff", "HOD", "Principal"
            role_map = {
                'AO': 'MANAGEMENT',
                'Staff': 'FACULTY',
                'HOD': 'HOD',
                'Principal': 'PRINCIPAL',
                'Admin': 'ADMIN'
            }
            expected_role = role_map.get(position)
            
            if user.role != expected_role:
                messages.error(request, "Selected position does not match your assigned role.")
            else:
                auth_login(request, user)
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid Mail id or password.")
            
    return render(request, 'registration/login.html')

def send_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email or not email.endswith('@drngpit.ac.in'):
            return JsonResponse({'status': 'error', 'message': 'Invalid Dr.NGPIT email'})
            
        try:
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Email not found in system'})
            
        otp = ''.join(random.choices(string.digits, k=5))
        OTP_STORE[email] = otp
        print(f"\n======================================")
        print(f"MOCK EMAIL SENT TO: {email}")
        print(f"YOUR OTP CODE IS: {otp}")
        print(f"======================================\n")
        
        return JsonResponse({'status': 'success', 'message': 'OTP sent successfully. Check server console.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def change_password_first_time(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('login')
            
        if email not in OTP_STORE or OTP_STORE[email] != otp:
            messages.error(request, "Invalid or expired OTP.")
            return redirect('login')
            
        try:
            user = User.objects.get(username=email)
            user.set_password(new_password)
            user.save()
            del OTP_STORE[email]
            messages.success(request, "Password changed successfully! You can now log in.")
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            
        return redirect('login')
        
@login_required
def dashboard(request):
    user = request.user
    context = {}
    
    if user.role == 'FACULTY':
        context['role_title'] = 'Faculty Dashboard'
    elif user.role == 'HOD':
        context['role_title'] = 'HOD Dashboard'
    elif user.role == 'MANAGEMENT':
        context['role_title'] = 'Management / AO Dashboard'
    elif user.role == 'PRINCIPAL':
        context['role_title'] = 'Principal Dashboard'
    elif user.role == 'ADMIN':
        context['role_title'] = 'Admin Dashboard'
        
    return render(request, 'accounts/dashboard.html', context)

@login_required
def manage_users(request):
    if request.user.role not in ['MANAGEMENT', 'ADMIN', 'HOD']:
        return redirect('dashboard')
        
    users = []
    if request.user.role == 'HOD':
        dept = request.user.hod_profile.department
        from departments.models import Faculty
        faculty_users = Faculty.objects.filter(department=dept).select_related('user')
        users = [f.user for f in faculty_users]
    elif request.user.role in ['ADMIN', 'MANAGEMENT']:
        users = User.objects.exclude(username='admin')
        
    from departments.models import Department
    departments = Department.objects.all()
    
    if request.method == 'POST' and request.user.role == 'MANAGEMENT':
        action = request.POST.get('action')
        
        if action == 'delete':
            user_id = request.POST.get('user_id')
            user_to_del = get_object_or_404(User, id=user_id)
            if user_to_del.is_superuser or user_to_del.role in ['ADMIN', 'PRINCIPAL']:
                messages.error(request, "Cannot delete this high-level user.")
            else:
                user_to_del.delete()
                messages.success(request, "User deleted successfully.")
            return redirect('manage_users')
            
        elif action == 'edit':
            user_id = request.POST.get('user_id')
            new_dept_id = request.POST.get('department')
            new_position = request.POST.get('position') # 'Staff' or 'HOD'
            user_to_edit = get_object_or_404(User, id=user_id)
            
            if user_to_edit.is_superuser or user_to_edit.role in ['ADMIN', 'PRINCIPAL']:
                messages.error(request, "Cannot edit this high-level user.")
                return redirect('manage_users')
                
            role_map = {'Staff': 'FACULTY', 'HOD': 'HOD'}
            new_role = role_map.get(new_position, 'FACULTY')
            
            user_to_edit.role = new_role
            user_to_edit.save()
            
            dept = Department.objects.get(id=new_dept_id)
            
            # Clean up old profiles
            from departments.models import Faculty, HOD
            Faculty.objects.filter(user=user_to_edit).delete()
            HOD.objects.filter(user=user_to_edit).delete()
            
            # Create new profile
            if new_role == 'FACULTY':
                Faculty.objects.create(user=user_to_edit, department=dept, designation='Staff', contact_number='')
            elif new_role == 'HOD':
                HOD.objects.create(user=user_to_edit, department=dept)
                
            messages.success(request, f"User {user_to_edit.email} updated successfully.")
            return redirect('manage_users')
            
        else:
            # Add staff
            staff_email = request.POST.get('staff_email')
            position = request.POST.get('position')
            department_id = request.POST.get('department')
            
            if not staff_email.endswith('@drngpit.ac.in'):
                messages.error(request, "Mail id must end with @drngpit.ac.in")
                return redirect('manage_users')
                
            if User.objects.filter(username=staff_email).exists():
                messages.error(request, "User with this email already exists.")
                return redirect('manage_users')
                
            role_map = {'Staff': 'FACULTY', 'HOD': 'HOD'}
            new_role = role_map.get(position, 'FACULTY')
            
            new_user = User.objects.create(username=staff_email, email=staff_email, role=new_role)
            new_user.set_password('drngp@123')
            new_user.save()
            
            dept = Department.objects.get(id=department_id)
            if new_role == 'FACULTY':
                from departments.models import Faculty
                Faculty.objects.create(user=new_user, department=dept, designation='Staff', contact_number='')
            elif new_role == 'HOD':
                from departments.models import HOD
                HOD.objects.create(user=new_user, department=dept)
                
            messages.success(request, f"Staff {staff_email} added successfully. Default password is drngp@123")
            return redirect('manage_users')
        
    return render(request, 'accounts/manage_users.html', {'users_list': users, 'departments': departments})
