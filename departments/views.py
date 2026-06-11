from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Department

@login_required
def manage_departments(request):
    if request.user.role not in ['MANAGEMENT', 'ADMIN']:
        messages.error(request, "Permission denied.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        dept_id = request.POST.get('dept_id')
        if 'delete' in request.POST and dept_id:
            Department.objects.filter(id=dept_id).delete()
            messages.success(request, "Department deleted.")
        else:
            name = request.POST.get('department_name')
            code = request.POST.get('department_code')
            
            if dept_id:
                dept = get_object_or_404(Department, id=dept_id)
                dept.department_name = name
                dept.department_code = code
                dept.save()
                messages.success(request, "Department updated.")
            else:
                if Department.objects.filter(department_code=code).exists():
                    messages.error(request, f"Department code {code} already exists.")
                else:
                    Department.objects.create(department_name=name, department_code=code)
                    messages.success(request, "Department created.")
        return redirect('manage_departments')
        
    departments = Department.objects.all()
    return render(request, 'departments/manage_departments.html', {'departments': departments})
