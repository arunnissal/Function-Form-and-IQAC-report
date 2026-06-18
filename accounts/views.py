from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, update_session_auth_hash
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import get_user_model
import random
import string

User = get_user_model()

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
def change_password(request):
    if request.method == 'POST' and 'change_password' in request.POST:
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not request.user.check_password(current_password):
            messages.error(request, "Incorrect current password.")
        elif new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
        else:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Password updated successfully!")
            
    next_url = request.POST.get('next', 'dashboard')
    return redirect(next_url)

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
    
    selected_dept_id = request.GET.get('department', '')
    
    if request.user.role in ['ADMIN', 'MANAGEMENT']:
        if selected_dept_id:
            filtered_users = []
            for u in users:
                if u.role == 'FACULTY' and hasattr(u, 'faculty_profile') and str(u.faculty_profile.department_id) == selected_dept_id:
                    filtered_users.append(u)
                elif u.role == 'HOD' and hasattr(u, 'hod_profile') and str(u.hod_profile.department_id) == selected_dept_id:
                    filtered_users.append(u)
            users = filtered_users
    
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
            
        elif action == 'reset_password':
            user_id = request.POST.get('user_id')
            user_to_reset = get_object_or_404(User, id=user_id)
            
            if user_to_reset.is_superuser or user_to_reset.role in ['ADMIN', 'PRINCIPAL']:
                messages.error(request, "Cannot reset password for this high-level user.")
            else:
                default_password = user_to_reset.email.split('@')[0]
                user_to_reset.set_password(default_password)
                user_to_reset.save()
                messages.success(request, f"Password reset to '{default_password}' for {user_to_reset.email}")
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
            
        elif action == 'bulk_add':
            excel_file = request.FILES.get('excel_file')
            if not excel_file:
                messages.error(request, "Please upload an Excel file.")
                return redirect('manage_users')
            
            try:
                import pandas as pd
                df = pd.read_excel(excel_file)
                
                required_cols = ['Full Name', 'Email', 'Department Code', 'Position']
                if not all(col in df.columns for col in required_cols):
                    messages.error(request, f"Excel file must contain columns: {', '.join(required_cols)}")
                    return redirect('manage_users')
                
                success_count = 0
                error_count = 0
                
                for index, row in df.iterrows():
                    full_name = str(row.get('Full Name', '')).strip()
                    staff_email = str(row.get('Email', '')).strip()
                    dept_code = str(row.get('Department Code', '')).strip()
                    position = str(row.get('Position', '')).strip()
                    
                    if not staff_email or pd.isna(staff_email) or staff_email == 'nan':
                        continue
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
                    
                    new_user = User.objects.create(
                        username=staff_email, 
                        email=staff_email, 
                        role=new_role,
                        first_name=first_name,
                        last_name=last_name,
                        is_active=True
                    )
                    
                    default_password = staff_email.split('@')[0]
                    new_user.set_password(default_password)
                    new_user.save()
                    
                    if new_role == 'FACULTY':
                        from departments.models import Faculty
                        Faculty.objects.create(user=new_user, department=dept, designation='Staff', contact_number='')
                    elif new_role == 'HOD':
                        from departments.models import HOD
                        HOD.objects.create(user=new_user, department=dept)
                        
                    success_count += 1
                    
                if success_count > 0:
                    messages.success(request, f"Successfully bulk added {success_count} staff members.")
                if error_count > 0:
                    messages.warning(request, f"Skipped {error_count} rows due to duplicate emails, invalid emails, or unknown department codes.")
                    
            except Exception as e:
                messages.error(request, f"Error processing Excel file: {str(e)}")
            return redirect('manage_users')
            
        else:
            # Add staff
            full_name = request.POST.get('full_name')
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
            
            first_name = full_name.split()[0] if full_name else ''
            last_name = ' '.join(full_name.split()[1:]) if full_name and len(full_name.split()) > 1 else ''
            
            new_user = User.objects.create(
                username=staff_email, 
                email=staff_email, 
                role=new_role,
                first_name=first_name,
                last_name=last_name,
                is_active=True
            )
            
            default_password = staff_email.split('@')[0]
            new_user.set_password(default_password)
            new_user.save()
            
            dept = Department.objects.get(id=department_id)
            if new_role == 'FACULTY':
                from departments.models import Faculty
                Faculty.objects.create(user=new_user, department=dept, designation='Staff', contact_number='')
            elif new_role == 'HOD':
                from departments.models import HOD
                HOD.objects.create(user=new_user, department=dept)
                
            messages.success(request, f"Staff {staff_email} added successfully. Default password is {default_password}")
            return redirect('manage_users')
        
    return render(request, 'accounts/manage_users.html', {'users_list': users, 'departments': departments, 'selected_dept_id': selected_dept_id})

@login_required
def download_staff_template(request):
    import pandas as pd
    from django.http import HttpResponse
    from io import BytesIO
    
    df = pd.DataFrame({
        'Full Name': ['John Doe', 'Jane Smith'],
        'Email': ['johndoe@drngpit.ac.in', 'janesmith@drngpit.ac.in'],
        'Department Code': ['CSE', 'ECE'],
        'Position': ['Staff', 'HOD']
    })
    
    with BytesIO() as b:
        with pd.ExcelWriter(b, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Template')
        
        response = HttpResponse(
            b.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="staff_bulk_add_template.xlsx"'
        return response
