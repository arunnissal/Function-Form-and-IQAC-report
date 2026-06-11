from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def reports_dashboard(request):
    return render(request, 'reports/dashboard.html')
