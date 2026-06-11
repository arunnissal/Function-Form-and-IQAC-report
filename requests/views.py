from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import FunctionRequest
from halls.models import SeminarHall
from departments.models import Faculty
from resources.models import GuestHouseRequirement, RefreshmentRequirement, TransportRequirement, PowerCameraRequirement, MementoRequirement
from datetime import datetime

@login_required
def create_request(request):
    # Only faculty and HOD should create requests
    if request.user.role not in ['FACULTY', 'HOD']:
        messages.error(request, "You do not have permission to create requests.")
        return redirect('dashboard')
        
    try:
        faculty = request.user.faculty_profile
    except Faculty.DoesNotExist:
        try:
            # If user is HOD, maybe they are acting as faculty or they don't have faculty profile.
            # Assuming HOD can't create requests unless they have a faculty profile or we map it differently.
            # Let's map it via HOD profile department for simplicity
            department = request.user.hod_profile.department
            faculty = None # Or create a mock faculty profile
        except:
            messages.error(request, "User profile is not properly configured with a department.")
            return redirect('dashboard')

    if request.method == 'POST':
        # Step 1
        function_name = request.POST.get('function_name')
        function_type = request.POST.get('function_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        number_of_days = request.POST.get('number_of_days', 1)
        time_from = request.POST.get('time_from')
        time_to = request.POST.get('time_to')
        venue_id = request.POST.get('venue')
        
        venue = None
        if venue_id:
            venue = SeminarHall.objects.filter(id=venue_id).first()
            
            # Hard validation for venue conflicts
            conflicts = FunctionRequest.objects.filter(
                venue=venue, 
                start_date=start_date, 
                status__in=['APPROVED', 'PENDING_HOD', 'PENDING_MANAGEMENT', 'PENDING_PRINCIPAL']
            )
            
            has_conflict = False
            try:
                # Convert string times to time objects for comparison
                new_start_time = datetime.strptime(time_from, '%H:%M').time()
                new_end_time = datetime.strptime(time_to, '%H:%M').time()
                
                for c in conflicts:
                    if c.time_from < new_end_time and c.time_to > new_start_time:
                        has_conflict = True
                        break
            except Exception as e:
                pass # Fallback if time parsing fails
                
            if has_conflict:
                messages.error(request, "Error: The selected venue is already booked for this specific time slot!")
                halls = SeminarHall.objects.all()
                return render(request, 'requests/create_request.html', {'halls': halls, 'selected_venue_id': venue_id})
        
        # Determine department
        dept = faculty.department if faculty else department

        func_request = FunctionRequest.objects.create(
            faculty=faculty,
            department=dept,
            status='PENDING_HOD', # Initial status
            function_name=function_name,
            function_type=function_type,
            start_date=start_date,
            end_date=end_date,
            number_of_days=number_of_days,
            time_from=time_from,
            time_to=time_to,
            venue=venue,
            type_of_training=request.POST.get('type_of_training', ''),
            number_of_students=request.POST.get('number_of_students', 0) or 0,
            class_name=request.POST.get('class_name', ''),
            organizer_name=request.POST.get('organizer_name', ''),
            organizer_contact=request.POST.get('organizer_contact', ''),
            chief_guest_name=request.POST.get('chief_guest_name', ''),
            chief_guest_designation=request.POST.get('chief_guest_designation', ''),
            chief_guest_organization=request.POST.get('chief_guest_organization', ''),
        )
        
        # Step 2: Guest House
        GuestHouseRequirement.objects.create(
            function_request=func_request,
            required=request.POST.get('guest_house_required') == 'on',
            number_of_persons=request.POST.get('gh_persons') or 0,
            from_date=request.POST.get('gh_from_date') or None,
            to_date=request.POST.get('gh_to_date') or None
        )
        
        # Step 3: Refreshments
        RefreshmentRequirement.objects.create(
            function_request=func_request,
            tea_required=request.POST.get('tea_required') == 'on',
            coffee_required=request.POST.get('coffee_required') == 'on',
            snacks_required=request.POST.get('snacks_required') == 'on',
            veg_lunch_count=request.POST.get('veg_lunch_count') or 0,
            non_veg_lunch_count=request.POST.get('non_veg_lunch_count') or 0,
            tiffin_count=request.POST.get('tiffin_count') or 0,
            required_time=request.POST.get('ref_required_time') or None,
            payment_through=request.POST.get('payment_through', '')
        )
        
        # Step 4: Transport
        TransportRequirement.objects.create(
            function_request=func_request,
            required=request.POST.get('transport_required') == 'on',
            date=request.POST.get('tr_date') or None,
            pickup_location=request.POST.get('tr_location', ''),
            pickup_time=request.POST.get('tr_pickup_time') or None,
            drop_time=request.POST.get('tr_drop_time') or None,
            pickup_person_name=request.POST.get('tr_pickup_person', ''),
            pickup_person_contact=request.POST.get('tr_pickup_contact', '')
        )
        
        # Step 5: Power / Camera
        PowerCameraRequirement.objects.create(
            function_request=func_request,
            mic_required=request.POST.get('mic_required') == 'on',
            mic_type=request.POST.get('mic_type', ''),
            number_of_mics=request.POST.get('number_of_mics') or 0,
            ac_required=request.POST.get('ac_required') == 'on',
            projector_required=request.POST.get('projector_required') == 'on',
            laptop_required=request.POST.get('laptop_required') == 'on',
            photographer_required=request.POST.get('photographer_required') == 'on',
            photographer_type=request.POST.get('photographer_type', '')
        )
        
        # Step 6: Memento
        MementoRequirement.objects.create(
            function_request=func_request,
            required=request.POST.get('memento_required') == 'on',
            honorarium_worth=request.POST.get('honorarium_worth', ''),
            quantity=request.POST.get('memento_quantity') or 0,
            dias_seats=request.POST.get('dias_seats') or 0,
            audience_seats=request.POST.get('audience_seats') or 0,
            table_cloths=request.POST.get('table_cloths') or 0,
            reception_items=request.POST.get('reception_items', '')
        )

        messages.success(request, "Function request submitted successfully!")
        return redirect('my_requests')

    halls = SeminarHall.objects.all()
    selected_venue_id = request.GET.get('venue', '')
    return render(request, 'requests/create_request.html', {'halls': halls, 'selected_venue_id': selected_venue_id})

@login_required
def my_requests(request):
    if request.user.role == 'FACULTY':
        reqs = FunctionRequest.objects.filter(faculty__user=request.user).order_by('-created_at')
    elif request.user.role == 'HOD':
        reqs = FunctionRequest.objects.filter(department=request.user.hod_profile.department).order_by('-created_at')
    elif request.user.role in ['MANAGEMENT', 'PRINCIPAL', 'ADMIN']:
        from approvals.models import ApprovalLog
        approved_req_ids = ApprovalLog.objects.filter(
            approver=request.user, 
            status='APPROVED'
        ).values_list('function_request_id', flat=True)
        reqs = FunctionRequest.objects.filter(id__in=approved_req_ids).order_by('-created_at')
    else:
        reqs = FunctionRequest.objects.none()
        
    return render(request, 'requests/my_requests.html', {'requests': reqs})
