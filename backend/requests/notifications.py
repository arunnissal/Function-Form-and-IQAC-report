import logging
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.conf import settings
from departments.models import HOD

logger = logging.getLogger(__name__)
User = get_user_model()

def send_hod_submission_notification(req):
    """
    Notifies the HOD of the requesting department when a Faculty submits a new request.
    """
    try:
        hod = HOD.objects.filter(department=req.department).first()
        if not hod or not hod.user.email:
            logger.warning(f"No HOD user/email found for department {req.department.department_code}")
            return
        
        subject = f"[Function Requirement] New Request #{req.id} Submitted for Approval"
        body = (
            f"Dear HOD,\n\n"
            f"A new function requirement request has been submitted by {req.faculty.user.get_full_name() or req.faculty.user.username} "
            f"for your department ({req.department.department_name}).\n\n"
            f"Request Details:\n"
            f"- Request ID: #{req.id}\n"
            f"- Event/Function Title: {req.function_name}\n"
            f"- Department: {req.department.department_code}\n"
            f"- Event Date: {req.start_date}\n"
            f"- Current Workflow Stage: Pending HOD Approval\n"
            f"- Required Action: Please log in to review and approve/reject the request.\n\n"
            f"Regards,\n"
            f"Function Requirement System"
        )
        
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [hod.user.email],
            fail_silently=False,
        )
        logger.info(f"Notification email sent to HOD {hod.user.email} for request #{req.id}")
    except Exception as e:
        logger.exception(f"Failed to send HOD submission notification for request #{req.id}: {e}")

def send_dean_notification(req):
    """
    Notifies the Dean of Computing when a request enters PENDING_DEAN stage.
    """
    try:
        dean_users = User.objects.filter(role='DEAN_COMPUTING')
        recipients = [u.email for u in dean_users if u.email]
        if not recipients:
            logger.warning("No Dean users with email found.")
            return

        subject = f"[Function Requirement] Action Required: Review Computing Request #{req.id}"
        body = (
            f"Dear Dean of Computing,\n\n"
            f"Request #{req.id} for the event '{req.function_name}' has been approved by the HOD "
            f"and is awaiting your review.\n\n"
            f"Request Details:\n"
            f"- Request ID: #{req.id}\n"
            f"- Event/Function Title: {req.function_name}\n"
            f"- Department: {req.department.department_code}\n"
            f"- Event Date: {req.start_date}\n"
            f"- Current Workflow Stage: Pending Dean Approval\n"
            f"- Required Action: Please log in to review and approve/reject the request.\n\n"
            f"Regards,\n"
            f"Function Requirement System"
        )
        
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            recipients,
            fail_silently=False,
        )
        logger.info(f"Notification email sent to Dean users {recipients} for request #{req.id}")
    except Exception as e:
        logger.exception(f"Failed to send Dean notification for request #{req.id}: {e}")

def send_management_notification(req):
    """
    Notifies Management AO when a request enters PENDING_MANAGEMENT stage.
    """
    try:
        management_users = User.objects.filter(role='MANAGEMENT')
        recipients = [u.email for u in management_users if u.email]
        if not recipients:
            logger.warning("No Management users with email found.")
            return

        subject = f"[Function Requirement] Action Required: Allocate Hall/Logistics for Request #{req.id}"
        body = (
            f"Dear Management,\n\n"
            f"Request #{req.id} for the event '{req.function_name}' has been approved by the HOD/Dean "
            f"and is awaiting venue and logistics allocation.\n\n"
            f"Request Details:\n"
            f"- Request ID: #{req.id}\n"
            f"- Event/Function Title: {req.function_name}\n"
            f"- Department: {req.department.department_code}\n"
            f"- Event Date: {req.start_date}\n"
            f"- Current Workflow Stage: Pending Management Approval\n"
            f"- Required Action: Please log in to assign a venue and approve logistics.\n\n"
            f"Regards,\n"
            f"Function Requirement System"
        )
        
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            recipients,
            fail_silently=False,
        )
        logger.info(f"Notification email sent to Management users {recipients} for request #{req.id}")
    except Exception as e:
        logger.exception(f"Failed to send Management notification for request #{req.id}: {e}")

def send_principal_notification(req):
    """
    Notifies the Principal when a request enters PENDING_PRINCIPAL stage.
    """
    try:
        principal_users = User.objects.filter(role='PRINCIPAL')
        recipients = [u.email for u in principal_users if u.email]
        if not recipients:
            logger.warning("No Principal users with email found.")
            return

        subject = f"[Function Requirement] Action Required: Final Review for Request #{req.id}"
        body = (
            f"Dear Principal,\n\n"
            f"Request #{req.id} for the event '{req.function_name}' has been processed by Management "
            f"and is awaiting your final executive approval.\n\n"
            f"Request Details:\n"
            f"- Request ID: #{req.id}\n"
            f"- Event/Function Title: {req.function_name}\n"
            f"- Department: {req.department.department_code}\n"
            f"- Venue Allocated: {req.venue.hall_name if req.venue else 'None'}\n"
            f"- Event Date: {req.start_date}\n"
            f"- Current Workflow Stage: Pending Principal Approval\n"
            f"- Required Action: Please log in to review and grant/reject approval.\n\n"
            f"Regards,\n"
            f"Function Requirement System"
        )
        
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            recipients,
            fail_silently=False,
        )
        logger.info(f"Notification email sent to Principal users {recipients} for request #{req.id}")
    except Exception as e:
        logger.exception(f"Failed to send Principal notification for request #{req.id}: {e}")

def send_management_confirmation_notification(req):
    """
    Notifies Management when the Principal approves a request and it shifts to PENDING_FINAL_CONFIRMATION.
    """
    try:
        management_users = User.objects.filter(role='MANAGEMENT')
        recipients = [u.email for u in management_users if u.email]
        if not recipients:
            logger.warning("No Management/AO users with email found.")
            return
        
        subject = f"[Function Requirement] Action Required: Final Confirmation for Request #{req.id}"
        body = (
            f"Dear Management / Academic Office,\n\n"
            f"Request #{req.id} for the event '{req.function_name}' has been approved by the Principal "
            f"and is now awaiting your final booking confirmation.\n\n"
            f"Request Details:\n"
            f"- Request ID: #{req.id}\n"
            f"- Event/Function Title: {req.function_name}\n"
            f"- Department: {req.department.department_code}\n"
            f"- Venue Assigned: {req.venue.hall_name if req.venue else 'None'}\n"
            f"- Event Date: {req.start_date}\n"
            f"- Current Workflow Stage: Pending Final Confirmation\n"
            f"- Required Action: Please log in to confirm the seminar hall booking.\n\n"
            f"Regards,\n"
            f"Function Requirement System"
        )
        
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            recipients,
            fail_silently=False,
        )
        logger.info(f"Notification email sent to Management users {recipients} for request #{req.id}")
    except Exception as e:
        logger.exception(f"Failed to send Management confirmation notification for request #{req.id}: {e}")

def send_faculty_confirmed_notification(req):
    """
    Notifies the Faculty owner that their request booking is officially APPROVED.
    """
    try:
        recipient = req.faculty.user.email
        if not recipient:
            logger.warning(f"No Faculty user email found for request #{req.id}")
            return

        subject = f"[Function Requirement] APPROVED: Booking Confirmed for Request #{req.id}"
        body = (
            f"Dear {req.faculty.user.get_full_name() or req.faculty.user.username},\n\n"
            f"We are pleased to inform you that your request #{req.id} for the event '{req.function_name}' "
            f"has been fully approved and confirmed.\n\n"
            f"Booking Details:\n"
            f"- Request ID: #{req.id}\n"
            f"- Event/Function Title: {req.function_name}\n"
            f"- Department: {req.department.department_code}\n"
            f"- Confirmed Venue: {req.venue.hall_name if req.venue else 'None'}\n"
            f"- Event Date: {req.start_date}\n"
            f"- Status: APPROVED (Officially Reserved)\n\n"
            f"Regards,\n"
            f"Function Requirement System"
        )
        
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )
        logger.info(f"Booking confirmation email sent to Faculty {recipient} for request #{req.id}")
    except Exception as e:
        logger.exception(f"Failed to send Faculty confirmation notification for request #{req.id}: {e}")

def send_faculty_correction_notification(req, remarks=""):
    """
    Notifies Faculty that their request has been returned for correction.
    """
    try:
        recipient = req.faculty.user.email
        if not recipient:
            logger.warning(f"No Faculty user email found for request #{req.id}")
            return

        subject = f"[Function Requirement] Action Required: Request #{req.id} Returned for Correction"
        body = (
            f"Dear {req.faculty.user.get_full_name() or req.faculty.user.username},\n\n"
            f"Your request #{req.id} for the event '{req.function_name}' has been returned for correction.\n\n"
            f"Details:\n"
            f"- Request ID: #{req.id}\n"
            f"- Event/Function Title: {req.function_name}\n"
            f"- Status: RETURNED_FOR_CORRECTION\n"
            f"- Remarks / Reason: {remarks or 'No remarks provided.'}\n\n"
            f"Required Action: Please log in, update the requested details, and resubmit.\n\n"
            f"Regards,\n"
            f"Function Requirement System"
        )
        
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )
        logger.info(f"Correction email sent to Faculty {recipient} for request #{req.id}")
    except Exception as e:
        logger.exception(f"Failed to send Faculty correction notification for request #{req.id}: {e}")

def send_faculty_rejection_notification(req, remarks=""):
    """
    Notifies Faculty that their request has been rejected.
    """
    try:
        recipient = req.faculty.user.email
        if not recipient:
            logger.warning(f"No Faculty user email found for request #{req.id}")
            return

        subject = f"[Function Requirement] REJECTED: Request #{req.id} Has Been Rejected"
        body = (
            f"Dear {req.faculty.user.get_full_name() or req.faculty.user.username},\n\n"
            f"We regret to inform you that your request #{req.id} for the event '{req.function_name}' "
            f"has been rejected by the reviewing authority.\n\n"
            f"Details:\n"
            f"- Request ID: #{req.id}\n"
            f"- Event/Function Title: {req.function_name}\n"
            f"- Status: REJECTED\n"
            f"- Remarks / Reason: {remarks or 'No remarks provided.'}\n\n"
            f"Regards,\n"
            f"Function Requirement System"
        )
        
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )
        logger.info(f"Rejection email sent to Faculty {recipient} for request #{req.id}")
    except Exception as e:
        logger.exception(f"Failed to send Faculty rejection notification for request #{req.id}: {e}")

def send_cancellation_notification(req, remarks=""):
    """
    Notifies the Faculty owner, department HOD, and Management when a request is cancelled.
    """
    try:
        recipients = set()
        
        # Faculty Owner
        if req.faculty.user.email:
            recipients.add(req.faculty.user.email)
            
        # HOD
        hod = HOD.objects.filter(department=req.department).first()
        if hod and hod.user.email:
            recipients.add(hod.user.email)
            
        # Management
        management_users = User.objects.filter(role='MANAGEMENT')
        for u in management_users:
            if u.email:
                recipients.add(u.email)
                
        recipients_list = list(recipients)
        if not recipients_list:
            logger.warning(f"No stakeholders found with emails for request #{req.id} cancellation")
            return

        subject = f"[Function Requirement] CANCELLED: Request #{req.id} Has Been Cancelled"
        body = (
            f"Dear Stakeholder,\n\n"
            f"Please be informed that the event request #{req.id} ('{req.function_name}') "
            f"has been cancelled, and any reserved venues have been released.\n\n"
            f"Cancellation Details:\n"
            f"- Request ID: #{req.id}\n"
            f"- Event/Function Title: {req.function_name}\n"
            f"- Department: {req.department.department_code}\n"
            f"- Venue Released: {req.venue.hall_name if req.venue else 'None'}\n"
            f"- Status: CANCELLED\n"
            f"- Remarks: {remarks or 'Cancelled due to administrative reasons.'}\n\n"
            f"Regards,\n"
            f"Function Requirement System"
        )
        
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            recipients_list,
            fail_silently=False,
        )
        logger.info(f"Cancellation email sent to {recipients_list} for request #{req.id}")
    except Exception as e:
        logger.exception(f"Failed to send cancellation notification for request #{req.id}: {e}")

def send_resubmission_notification(req, target_status):
    """
    Notifies the target reviewer when Faculty resubmits a request.
    """
    if target_status == 'PENDING_HOD':
        send_hod_submission_notification(req)
    elif target_status == 'PENDING_DEAN':
        send_dean_notification(req)
    elif target_status == 'PENDING_MANAGEMENT':
        send_management_notification(req)
    elif target_status == 'PENDING_PRINCIPAL':
        send_principal_notification(req)
    elif target_status == 'PENDING_FINAL_CONFIRMATION':
        send_management_confirmation_notification(req)
