from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from requests.models import FunctionRequest
from .models import EventReport, ReportGuest
from .views import generate_iqac_pdf  # We can just call the existing PDF logic!

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def iqac_report_api(request, req_id):
    func_req = get_object_or_404(FunctionRequest, id=req_id)
    
    if request.method == 'GET':
        report = EventReport.objects.filter(function_request=func_req).first()
        if not report:
            return Response({"error": "Report not found"}, status=404)
        # return basic info
        guests = ReportGuest.objects.filter(event_report=report)
        guests_data = [{"name": g.name, "designation": g.designation, "organization_address": g.organization_address, "mobile": g.mobile, "email": g.email, "topic": g.topic} for g in guests]
        return Response({
            "dept_ref_no": report.dept_ref_no,
            "objective": report.objective,
            "funding_agency": report.funding_agency,
            "alumni_contribution": report.alumni_contribution,
            "budget_proposed": report.budget_proposed,
            "budget_actual": report.budget_actual,
            "participants_internal": report.participants_internal,
            "participants_external": report.participants_external,
            "outcome": report.outcome,
            "guests": guests_data
        })

    # POST - Fill IQAC Report
    if request.user.role not in ['FACULTY', 'HOD']:
        return Response({"error": "Only Faculty and HOD can fill the report."}, status=403)
        
    if func_req.faculty.user != request.user and request.user.role != 'HOD':
        return Response({"error": "You can only fill reports for your own booked events."}, status=403)

    if func_req.status != 'APPROVED':
        return Response({"error": "Event is not approved."}, status=400)

    report, _ = EventReport.objects.get_or_create(function_request=func_req)

    data = request.data
    report.dept_ref_no = data.get('dept_ref_no', report.dept_ref_no)
    report.objective = data.get('objective', report.objective)
    report.funding_agency = data.get('funding_agency', report.funding_agency)
    report.alumni_contribution = data.get('alumni_contribution', report.alumni_contribution)
    report.budget_proposed = data.get('budget_proposed', report.budget_proposed)
    report.budget_actual = data.get('budget_actual', report.budget_actual)
    report.participants_internal = data.get('participants_internal', report.participants_internal)
    report.participants_external = data.get('participants_external', report.participants_external)
    report.outcome = data.get('outcome', report.outcome)

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

    # Dynamic guests
    guests_json = data.get('guests', '[]')
    import json
    try:
        guests_list = json.loads(guests_json)
        if isinstance(guests_list, list) and len(guests_list) > 0:
            ReportGuest.objects.filter(event_report=report).delete()
            for g in guests_list:
                ReportGuest.objects.create(
                    event_report=report,
                    name=g.get('name', ''),
                    designation=g.get('designation', ''),
                    organization_address=g.get('organization_address', ''),
                    mobile=g.get('mobile', ''),
                    email=g.get('email', ''),
                    topic=g.get('topic', '')
                )
    except:
        pass # ignore json parse error for simplicity

    return Response({"message": "IQAC Report saved successfully."})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_iqac_pdf_api(request, req_id):
    # Re-use the existing logic!
    try:
        return generate_iqac_pdf(request, req_id)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
