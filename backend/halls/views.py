from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SeminarHall
from requests.models import FunctionRequest
from datetime import date

@login_required
def manage_halls(request):
    if request.user.role not in ['MANAGEMENT', 'ADMIN']:
        messages.error(request, "Permission denied.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        hall_id = request.POST.get('hall_id')
        if 'delete' in request.POST and hall_id:
            SeminarHall.objects.filter(id=hall_id).delete()
            messages.success(request, "Hall deleted.")
        else:
            name = request.POST.get('hall_name')
            capacity = request.POST.get('capacity')
            location = request.POST.get('location')
            facilities = request.POST.get('facilities')
            
            if hall_id:
                hall = get_object_or_404(SeminarHall, id=hall_id)
                hall.hall_name = name
                hall.capacity = capacity
                hall.location = location
                hall.facilities = facilities
                hall.save()
                messages.success(request, "Hall updated.")
            else:
                SeminarHall.objects.create(
                    hall_name=name, capacity=capacity, location=location, facilities=facilities
                )
                messages.success(request, "Hall created.")
        return redirect('manage_halls')
        
    halls = SeminarHall.objects.all()
    return render(request, 'halls/manage_halls.html', {'halls': halls})


@login_required
def hall_availability(request):
    halls = SeminarHall.objects.all()
    
    # Get all approved bookings
    bookings = FunctionRequest.objects.filter(
        status='APPROVED',
        venue__isnull=False
    ).order_by('start_date')
    
    events_json = []
    for b in bookings:
        start_datetime = f"{b.start_date.isoformat()}T{b.time_from.strftime('%H:%M:%S')}"
        end_d = b.end_date if b.end_date else b.start_date
        end_datetime = f"{end_d.isoformat()}T{b.time_to.strftime('%H:%M:%S')}"
        
        events_json.append({
            'title': f"{b.function_name} ({b.venue.hall_name})",
            'start': start_datetime,
            'end': end_datetime,
            'description': f"Organizer: {b.organizer_name} | Dept: {b.department.department_code}"
        })
        
    import json
    return render(request, 'halls/availability.html', {
        'halls': halls,
        'events_json': json.dumps(events_json)
    })
