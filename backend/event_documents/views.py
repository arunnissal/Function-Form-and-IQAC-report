from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from requests.models import FunctionRequest
from .models import EventReport, ReportGuest

@login_required
def fill_iqac_report(request, req_id):
    func_req = get_object_or_404(FunctionRequest, id=req_id)
    
    # Check if user is the owner/faculty
    if request.user.role != 'FACULTY' and request.user.role != 'HOD':
        messages.error(request, "Permission denied.")
        return redirect('dashboard')
        
    if func_req.status != 'APPROVED':
        messages.error(request, "IQAC Report can only be generated for APPROVED events.")
        return redirect('my_requests')

    report, created = EventReport.objects.get_or_create(function_request=func_req)
    
    if created:
        # Pre-fill data from the Function Request to save time
        if func_req.number_of_students:
            report.participants_internal = str(func_req.number_of_students)
            report.save()
            
        if func_req.chief_guest_name:
            ReportGuest.objects.create(
                event_report=report,
                name=func_req.chief_guest_name,
                designation=func_req.chief_guest_designation,
                organization_address=func_req.chief_guest_organization
            )

    if request.method == 'POST':
        report.dept_ref_no = request.POST.get('dept_ref_no', '')
        report.objective = request.POST.get('objective', '')
        report.funding_agency = request.POST.get('funding_agency', '')
        report.alumni_contribution = request.POST.get('alumni_contribution', '')
        report.budget_proposed = request.POST.get('budget_proposed', '-')
        report.budget_actual = request.POST.get('budget_actual', '-')
        report.participants_internal = request.POST.get('participants_internal', '')
        report.participants_external = request.POST.get('participants_external', '')
        report.outcome = request.POST.get('outcome', '')
        
        if 'photo_1' in request.FILES:
            report.photo_1 = request.FILES['photo_1']
        if 'photo_2' in request.FILES:
            report.photo_2 = request.FILES['photo_2']
            
        if 'brochure' in request.FILES:
            report.brochure = request.FILES['brochure']
        if 'certificate' in request.FILES:
            report.certificate = request.FILES['certificate']
        if 'attendance_sheet' in request.FILES:
            report.attendance_sheet = request.FILES['attendance_sheet']
        if 'feedback_report' in request.FILES:
            report.feedback_report = request.FILES['feedback_report']
            
        report.save()
        
        # Handle dynamic guests
        # We can expect guest_name_1, guest_designation_1, etc.
        ReportGuest.objects.filter(event_report=report).delete() # clear old
        i = 1
        while True:
            name = request.POST.get(f'guest_name_{i}')
            if not name:
                break
            ReportGuest.objects.create(
                event_report=report,
                name=name,
                designation=request.POST.get(f'guest_designation_{i}', ''),
                organization_address=request.POST.get(f'guest_org_{i}', ''),
                mobile=request.POST.get(f'guest_mobile_{i}', ''),
                email=request.POST.get(f'guest_email_{i}', ''),
                topic=request.POST.get(f'guest_topic_{i}', '')
            )
            i += 1
            
        messages.success(request, "IQAC Report saved successfully. You can now generate the PDF.")
        return redirect('my_requests')

    return render(request, 'event_documents/fill_iqac_report.html', {'req': func_req, 'report': report})


from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from django.conf import settings
import os

@login_required
def generate_iqac_pdf(request, req_id):
    report = get_object_or_404(EventReport, function_request_id=req_id)
    func = report.function_request
    
    user_role = request.user.role
    if user_role not in ['FACULTY', 'HOD', 'MANAGEMENT', 'PRINCIPAL', 'ADMIN']:
        messages.error(request, "You do not have permission to download this report.")
        return redirect('dashboard')
        
    if user_role == 'HOD' and func.department != request.user.hod_profile.department:
        messages.error(request, "You can only download reports for your department.")
        return redirect('dashboard')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="IQAC_Report_{func.id}.pdf"'
    
    # We will build the PDF elements
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(name='TitleStyle', fontSize=14, alignment=1, spaceAfter=10, fontName='Helvetica-Bold')
    normal_style = styles['Normal']
    
    # Header
    elements.append(Paragraph("<b>Dr NGP Institute of Technology</b>", title_style))
    elements.append(Paragraph("<b>IQAC REPORT</b>", title_style))
    elements.append(Paragraph(f"<font color='red'><b>DEPARTMENT OF {func.department.department_name.upper()}</b></font>", title_style))
    elements.append(Spacer(1, 10))
    
    # Basic Data Table
    data = [
        ['Dept. Ref. No.: ' + report.dept_ref_no, 'Date: ' + str(func.start_date)],
        [Paragraph('Event Name: ' + func.function_type, normal_style), ''],
        [Paragraph('Event Title: ' + func.function_name, normal_style), ''],
        [Paragraph('Objective of the event: ' + report.objective, normal_style), ''],
        [Paragraph('Funding Agency (Int / Ext): ' + report.funding_agency, normal_style), ''],
        [Paragraph('Alumni Contribution (if any): ' + report.alumni_contribution, normal_style), ''],
        ['Venue: ' + (func.venue.hall_name if func.venue else 'N/A'), 'Date of event: ' + str(func.start_date)]
    ]
    
    # Budget and Participants
    data.append([
        Paragraph(f"<b>Budget (in INR)</b><br/>Proposed: {report.budget_proposed}<br/>Actual: {report.budget_actual}", normal_style),
        Paragraph(f"<b>Participant's details (in Nos.)</b><br/>Internal: {report.participants_internal}<br/>External: {report.participants_external}", normal_style)
    ])
    
    t = Table(data, colWidths=[3.5*inch, 3.5*inch])
    t.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('SPAN', (0, 1), (1, 1)),
        ('SPAN', (0, 2), (1, 2)),
        ('SPAN', (0, 3), (1, 3)),
        ('SPAN', (0, 4), (1, 4)),
        ('SPAN', (0, 5), (1, 5)),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t)
    
    # Guest Details
    guests = report.guests.all()
    if guests:
        elements.append(Paragraph("<b>Guest Details</b>", ParagraphStyle(name='SubTitle', fontSize=12, alignment=1, spaceBefore=5, spaceAfter=5, fontName='Helvetica-Bold')))
        for idx, guest in enumerate(guests, 1):
            guest_data = [
                [f"Guest {idx}", '', '', ''],
                ["Name", Paragraph(guest.name, normal_style), "Designation", Paragraph(guest.designation, normal_style)],
                ["Organization", Paragraph(guest.organization_address, normal_style), "Mobile / Landline", guest.mobile],
                ["", "", "Email Id", Paragraph(guest.email, normal_style)],
                ["Topic:", Paragraph(guest.topic, normal_style), '', '']
            ]
            gt = Table(guest_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
            gt.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('SPAN', (0,0), (3,0)), # Guest Header
                ('SPAN', (0,2), (0,3)), # Org span rows
                ('SPAN', (1,2), (1,3)), # Org val span rows
                ('SPAN', (0,4), (3,4)), # Topic span
                ('BACKGROUND', (0,0), (3,0), colors.lightgrey),
            ]))
            elements.append(gt)
    
    # Outcome & Photos
    elements.append(Spacer(1, 10))
    outcome_data = [
        ["Outcome of the event:"],
        [Paragraph(report.outcome, normal_style)],
        ["Picture of the event :"]
    ]
    
    # Add Photos
    photo_row = []
    if report.photo_1 and os.path.exists(report.photo_1.path):
        photo_row.append(RLImage(report.photo_1.path, width=3*inch, height=2*inch))
    else:
        photo_row.append("No Photo 1")
        
    if report.photo_2 and os.path.exists(report.photo_2.path):
        photo_row.append(RLImage(report.photo_2.path, width=3*inch, height=2*inch))
    else:
        photo_row.append("No Photo 2")
        
    outcome_data.append(photo_row)
    
    ot = Table(outcome_data, colWidths=[3.5*inch, 3.5*inch])
    ot.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('SPAN', (0,0), (1,0)),
        ('SPAN', (0,1), (1,1)),
        ('SPAN', (0,2), (1,2)),
        ('ALIGN', (0,3), (-1,3), 'CENTER'),
        ('VALIGN', (0,3), (-1,3), 'MIDDLE'),
    ]))
    elements.append(ot)
    
    # Footer
    elements.append(Spacer(1, 20))
    footer_data = [
        ["Event Coordinator", "IQAC Department Coordinator", "HoD"]
    ]
    ft = Table(footer_data, colWidths=[2.3*inch, 2.4*inch, 2.3*inch])
    ft.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    elements.append(ft)

    # Append Enclosures (Images)
    enclosures = [
        ("Brochure", report.brochure),
        ("Certificate", report.certificate),
        ("Attendance Sheet", report.attendance_sheet),
        ("Feedback Report", report.feedback_report)
    ]
    
    for enc_name, enc_file in enclosures:
        if enc_file and os.path.exists(enc_file.path):
            elements.append(PageBreak())
            elements.append(Paragraph(f"<b>{enc_name}</b>", title_style))
            elements.append(Spacer(1, 20))
            # Fit image to page width approximately
            elements.append(RLImage(enc_file.path, width=6*inch, height=8*inch, kind='proportional'))

    doc.build(elements)
    return response
