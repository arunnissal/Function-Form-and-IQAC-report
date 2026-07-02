from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from requests.models import FunctionRequest
from .models import ApprovalLog

@login_required
def approval_queue(request):
    role = request.user.role
    reqs = FunctionRequest.objects.none()
    
    if role == 'HOD':
        try:
            dept = request.user.hod_profile.department
            reqs = FunctionRequest.objects.filter(department=dept, status='PENDING_HOD').order_by('start_date')
        except:
            pass
    elif role == 'MANAGEMENT':
        reqs = FunctionRequest.objects.filter(status='PENDING_MANAGEMENT').order_by('start_date')
    elif role == 'PRINCIPAL':
        reqs = FunctionRequest.objects.filter(status='PENDING_PRINCIPAL').order_by('start_date')
    
    return render(request, 'approvals/approval_queue.html', {'requests': reqs})

@login_required
def request_detail(request, req_id):
    req = get_object_or_404(FunctionRequest, id=req_id)
    role = request.user.role
    
    if request.method == 'POST':
        action = request.POST.get('action')
        remarks = request.POST.get('remarks', '')
        
        if action == 'APPROVE':
            new_status = ''
            if role == 'HOD':
                new_status = 'PENDING_MANAGEMENT'
            elif role == 'MANAGEMENT':
                new_status = 'PENDING_PRINCIPAL'
            elif role == 'PRINCIPAL':
                new_status = 'APPROVED'
            
            req.status = new_status
            req.save()
            
            ApprovalLog.objects.create(
                function_request=req,
                approver=request.user,
                stage=role,
                status='APPROVED',
                remarks=remarks
            )
            messages.success(request, f"Request #{req.id} approved successfully.")
            return redirect('approval_queue')
            
        elif action == 'REJECT':
            req.status = 'REJECTED'
            req.save()
            
            ApprovalLog.objects.create(
                function_request=req,
                approver=request.user,
                stage=role,
                status='REJECTED',
                remarks=remarks
            )
            messages.success(request, f"Request #{req.id} rejected.")
            return redirect('approval_queue')

    can_approve = False
    if role == 'HOD' and req.status == 'PENDING_HOD':
        can_approve = True
    elif role == 'MANAGEMENT' and req.status == 'PENDING_MANAGEMENT':
        can_approve = True
    elif role == 'PRINCIPAL' and req.status == 'PENDING_PRINCIPAL':
        can_approve = True

    context = {
        'req': req,
        'can_approve': can_approve
    }
    return render(request, 'approvals/request_detail.html', context)

@login_required
def edit_request(request, req_id):
    req = get_object_or_404(FunctionRequest, id=req_id)
    role = request.user.role
    
    can_approve = False
    if role == 'HOD' and req.status == 'PENDING_HOD':
        can_approve = True
    elif role == 'MANAGEMENT' and req.status == 'PENDING_MANAGEMENT':
        can_approve = True
    elif role == 'PRINCIPAL' and req.status == 'PENDING_PRINCIPAL':
        can_approve = True
        
    if not can_approve:
        messages.error(request, "You do not have permission to edit this request at this stage.")
        return redirect('request_detail', req_id=req.id)
        
    if request.method == 'POST':
        # Guest House
        gh = req.guest_house
        gh.required = request.POST.get('guest_house_required') == 'on'
        gh.number_of_persons = request.POST.get('gh_persons') or 0
        gh.from_date = request.POST.get('gh_from_date') or None
        gh.to_date = request.POST.get('gh_to_date') or None
        gh.save()
        
        # Refreshment
        ref = req.refreshment
        ref.tea_required = request.POST.get('tea_required') == 'on'
        ref.coffee_required = request.POST.get('coffee_required') == 'on'
        ref.snacks_required = request.POST.get('snacks_required') == 'on'
        ref.veg_lunch_count = request.POST.get('veg_lunch_count') or 0
        ref.normal_lunch_count = request.POST.get('normal_lunch_count') or 0
        ref.non_veg_lunch_count = request.POST.get('non_veg_lunch_count') or 0
        ref.tiffin_count = request.POST.get('tiffin_count') or 0
        ref.required_time = request.POST.get('ref_required_time') or None
        ref.payment_through = request.POST.get('payment_through', '')
        ref.save()
        
        # Transport
        tr = req.transport
        tr.required = request.POST.get('transport_required') == 'on'
        tr.date = request.POST.get('tr_date') or None
        tr.pickup_location = request.POST.get('tr_location', '')
        tr.pickup_time = request.POST.get('tr_pickup_time') or None
        tr.drop_time = request.POST.get('tr_drop_time') or None
        tr.pickup_person_name = request.POST.get('tr_pickup_person', '')
        tr.pickup_person_contact = request.POST.get('tr_pickup_contact', '')
        tr.save()
        
        # Power / Camera
        pc = req.power_camera
        pc.mic_required = request.POST.get('mic_required') == 'on'
        pc.mic_type = request.POST.get('mic_type', '')
        pc.number_of_mics = request.POST.get('number_of_mics') or 0
        pc.ac_required = request.POST.get('ac_required') == 'on'
        pc.projector_required = request.POST.get('projector_required') == 'on'
        pc.laptop_required = request.POST.get('laptop_required') == 'on'
        pc.photographer_required = request.POST.get('photographer_required') == 'on'
        pc.photographer_type = request.POST.get('photographer_type', '')
        pc.save()
        
        # Memento
        mem = req.memento
        mem.required = request.POST.get('memento_required') == 'on'
        mem.honorarium_worth = request.POST.get('honorarium_worth', '')
        mem.quantity = request.POST.get('memento_quantity') or 0
        mem.dias_seats = request.POST.get('dias_seats') or 0
        mem.audience_seats = request.POST.get('audience_seats') or 0
        mem.table_cloths = request.POST.get('table_cloths') or 0
        mem.reception_items = request.POST.get('reception_items', '')
        mem.save()
        
        messages.success(request, "Request requirements updated successfully.")
        return redirect('request_detail', req_id=req.id)
        
    return render(request, 'approvals/edit_request.html', {'req': req})
