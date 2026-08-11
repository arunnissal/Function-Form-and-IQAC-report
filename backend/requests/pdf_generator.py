import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def get_related_attr(instance, relation_name):
    try:
        return getattr(instance, relation_name)
    except Exception:
        return None

def draw_page_decorations(canvas, doc):
    canvas.saveState()
    # Double-line border around both pages
    # Outer border: 20 points from the edge
    canvas.setLineWidth(1)
    canvas.rect(20, 20, doc.pagesize[0] - 40, doc.pagesize[1] - 40)
    # Inner border: 24 points from the edge (4 points gap)
    canvas.rect(24, 24, doc.pagesize[0] - 48, doc.pagesize[1] - 48)
    canvas.restoreState()

def generate_function_request_pdf(req):
    buffer = io.BytesIO()
    
    # 36pt (0.5 inch) margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Styles Setup
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        alignment=TA_CENTER,
        textColor=colors.black
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.black
    )
    
    sec_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.black
    )
    
    label_style = ParagraphStyle(
        'LabelText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=12,
        textColor=colors.black
    )
    
    bold_label_style = ParagraphStyle(
        'BoldLabelText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.black
    )

    value_style = ParagraphStyle(
        'ValueText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=colors.black
    )
    
    center_value_style = ParagraphStyle(
        'CenterValueText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.black
    )

    story = []
    
    # --- PAGE 1 ---
    
    # Header
    story.append(Paragraph("Dr. N.G.P. INSTITUTE OF TECHNOLOGY", title_style))
    story.append(Paragraph("(An Autonomous Institution)", subtitle_style))
    story.append(Paragraph("Coimbatore – 48", subtitle_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("FUNCTION REQUIREMENT FORM", title_style))
    story.append(Spacer(1, 10))
    
    # Department / Date Box
    dept_name = req.department.department_name if req.department else 'N/A'
    dept_code = req.department.department_code if req.department else 'N/A'
    date_val = req.start_date.strftime('%d-%m-%Y') if req.start_date else 'N/A'
    
    dept_box_data = [
        [
            Paragraph(f"<b>DEPARTMENT:</b> {dept_name} ({dept_code})", label_style),
            Paragraph(f"<b>DATE:</b> {date_val}", label_style)
        ]
    ]
    dept_box_table = Table(dept_box_data, colWidths=[360, 163])
    dept_box_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(dept_box_table)
    story.append(Spacer(1, 12))
    
    # Page 1 Fields 1-7
    days_count = f" ({req.number_of_days} Days)" if req.number_of_days else ""
    date_range = f"{req.start_date.strftime('%d-%m-%Y') if req.start_date else ''} to {req.end_date.strftime('%d-%m-%Y') if req.end_date else ''}{days_count}"
    time_val = f"From {req.time_from.strftime('%I:%M %p') if req.time_from else ''} To {req.time_to.strftime('%I:%M %p') if req.time_to else ''}"
    venue_val = req.venue.hall_name if req.venue else 'N/A'
    
    # Sub-table for students count and class
    students_class_data = [
        [
            Paragraph(str(req.number_of_students), value_style),
            Paragraph("<b>Class:</b>", label_style),
            Paragraph(req.class_name or '', value_style)
        ]
    ]
    students_class_table = Table(students_class_data, colWidths=[80, 50, 173])
    students_class_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (0, 0), 0.5, colors.black),
        ('LINEBELOW', (2, 0), (2, 0), 0.5, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))

    # Sub-table for designation and college
    designation_college_data = [
        [
            Paragraph(req.chief_guest_designation or '', value_style),
            Paragraph("<b>College / Industry:</b>", label_style),
            Paragraph(req.chief_guest_organization or '', value_style)
        ]
    ]
    designation_college_table = Table(designation_college_data, colWidths=[120, 100, 83])
    designation_college_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (0, 0), 0.5, colors.black),
        ('LINEBELOW', (2, 0), (2, 0), 0.5, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))

    fields_data = [
        [Paragraph("1. Name of the Function", label_style), Paragraph(req.function_name or '', value_style)],
        [Paragraph("2. Date & Number of Days", label_style), Paragraph(date_range, value_style)],
        [Paragraph("3. Time Duration", label_style), Paragraph(time_val, value_style)],
        [Paragraph("4. Venue", label_style), Paragraph(venue_val, value_style)],
        [Paragraph("5. Type of Training", label_style), Paragraph(req.type_of_training or '', value_style)],
        [Paragraph("    No. of Students", label_style), students_class_table],
        [Paragraph("    Transport Required for Students : Yes / No", label_style), Paragraph("", value_style)],
        [Paragraph("    If Yes, Name of the Stage & No. of Students", label_style), Paragraph("", value_style)],
        [Paragraph("6. Name of the Chief Guest", label_style), Paragraph(req.chief_guest_name or '', value_style)],
        [Paragraph("    Designation", label_style), designation_college_table],
        [Paragraph("7. Name and Contact Number of the Organizer", label_style), Paragraph(f"{req.organizer_name or ''} {f'({req.organizer_contact})' if req.organizer_contact else ''}", value_style)]
    ]
    
    fields_table = Table(fields_data, colWidths=[220, 303])
    # Apply underline bottom borders only for specific rows
    fields_table.setStyle(TableStyle([
        ('LINEBELOW', (1, 0), (1, 4), 0.5, colors.black),
        ('LINEBELOW', (1, 6), (1, 8), 0.5, colors.black),
        ('LINEBELOW', (1, 10), (1, 10), 0.5, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))
    story.append(fields_table)
    story.append(Spacer(1, 15))
    
    # Section: FACILITIES REQUIREMENT
    story.append(Paragraph("<u><b>FACILITIES REQUIREMENT</b></u>", sec_title_style))
    story.append(Spacer(1, 4))
    
    # (i) GUEST HOUSE
    story.append(Paragraph("<u><b>(i) GUEST HOUSE</b></u>", sec_title_style))
    story.append(Spacer(1, 4))
    
    gh = get_related_attr(req, 'guest_house')
    gh_required_str = "Yes [x]  No [ ]" if (gh and gh.required) else "Yes [ ]  No [x]"
    gh_persons = str(gh.number_of_persons) if (gh and gh.required and gh.number_of_persons) else ''
    gh_from = gh.from_date.strftime('%d-%m-%Y') if (gh and gh.required and gh.from_date) else ''
    gh_to = gh.to_date.strftime('%d-%m-%Y') if (gh and gh.required and gh.to_date) else ''
    
    gh_persons_data = [
        [
            Paragraph(gh_required_str, value_style),
            Paragraph("<b>If Yes: No. of Persons:</b>", label_style),
            Paragraph(gh_persons, value_style)
        ]
    ]
    gh_persons_table = Table(gh_persons_data, colWidths=[120, 120, 63])
    gh_persons_table.setStyle(TableStyle([
        ('LINEBELOW', (2, 0), (2, 0), 0.5, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))

    gh_days_data = [
        [
            Paragraph("From", label_style),
            Paragraph(gh_from, value_style),
            Paragraph("To", label_style),
            Paragraph(gh_to, value_style)
        ]
    ]
    gh_days_table = Table(gh_days_data, colWidths=[40, 100, 30, 133])
    gh_days_table.setStyle(TableStyle([
        ('LINEBELOW', (1, 0), (1, 0), 0.5, colors.black),
        ('LINEBELOW', (3, 0), (3, 0), 0.5, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))

    gh_data = [
        [Paragraph("Required", label_style), gh_persons_table],
        [Paragraph("No. of Days", label_style), gh_days_table]
    ]
    gh_table = Table(gh_data, colWidths=[220, 303])
    gh_table.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))
    story.append(gh_table)
    story.append(Spacer(1, 10))
    
    # (ii) REFRESEMENT / LUNCH
    story.append(Paragraph("<u><b>(ii) REFRESEMENT / LUNCH</b></u>", sec_title_style))
    story.append(Spacer(1, 4))
    
    ref = get_related_attr(req, 'refreshment')
    
    tea_chk = "[x]" if (ref and ref.tea_required) else "[ ]"
    coffee_chk = "[x]" if (ref and ref.coffee_required) else "[ ]"
    snacks_chk = "[x]" if (ref and ref.snacks_required) else "[ ]"
    
    ref_guest_str = f"Tea: {tea_chk}       Coffee: {coffee_chk}       Snacks: {snacks_chk}"
    ref_time = ref.required_time.strftime('%I:%M %p') if (ref and ref.required_time) else ''
    
    pmt_str = "Association Account [ ] / Institution Account [ ]"
    if ref and ref.payment_through:
        if ref.payment_through == 'ASSOCIATION':
            pmt_str = "Association Account [x] / Institution Account [ ]"
        elif ref.payment_through == 'INSTITUTION':
            pmt_str = "Association Account [ ] / Institution Account [x]"
            
    tiffin = str(ref.tiffin_count) if (ref and ref.tiffin_count) else ''
    lunch_normal = str(ref.normal_lunch_count) if (ref and ref.normal_lunch_count) else ''
    lunch_veg = str(ref.veg_lunch_count) if (ref and ref.veg_lunch_count) else ''
    lunch_nonveg = str(ref.non_veg_lunch_count) if (ref and ref.non_veg_lunch_count) else ''
    
    nos_data = [
        [
            Paragraph("Tiffin:", label_style), Paragraph(tiffin, value_style),
            Paragraph("Normal Lunch:", label_style), Paragraph(lunch_normal, value_style)
        ]
    ]
    nos_table = Table(nos_data, colWidths=[40, 80, 80, 103])
    nos_table.setStyle(TableStyle([
        ('LINEBELOW', (1, 0), (1, 0), 0.5, colors.black),
        ('LINEBELOW', (3, 0), (3, 0), 0.5, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))

    veg_nonveg_data = [
        [
            Paragraph(lunch_veg, value_style),
            Paragraph("Special Lunch (Non Veg):", label_style),
            Paragraph(lunch_nonveg, value_style)
        ]
    ]
    veg_nonveg_table = Table(veg_nonveg_data, colWidths=[80, 140, 83])
    veg_nonveg_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (0, 0), 0.5, colors.black),
        ('LINEBELOW', (2, 0), (2, 0), 0.5, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))

    ref_data = [
        [Paragraph("Refreshment for Guest", label_style), Paragraph(ref_guest_str, value_style)],
        [Paragraph("Required Time", label_style), Paragraph(ref_time, value_style)],
        [Paragraph("Refreshment for Students", label_style), Paragraph("Tea: [ ]       Coffee: [ ]       Snacks: [ ]", value_style)],
        [Paragraph("Required Time", label_style), Paragraph("", value_style)],
        [Paragraph("Payment Through", label_style), Paragraph(pmt_str, value_style)],
        [Paragraph("Mention the Exact Nos.", label_style), nos_table],
        [Paragraph("Special Lunch (Veg)", label_style), veg_nonveg_table],
        [Paragraph("Required Time", label_style), Paragraph("", value_style)]
    ]
    
    ref_table = Table(ref_data, colWidths=[220, 303])
    ref_table.setStyle(TableStyle([
        ('LINEBELOW', (1, 1), (1, 1), 0.5, colors.black),
        ('LINEBELOW', (1, 3), (1, 3), 0.5, colors.black),
        ('LINEBELOW', (1, 7), (1, 7), 0.5, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))
    story.append(ref_table)
    
    # Force page break after Refreshment section
    story.append(PageBreak())
    
    # --- PAGE 2 ---
    
    # Header repeats cleanly
    story.append(Paragraph("Dr. N.G.P. INSTITUTE OF TECHNOLOGY", title_style))
    story.append(Paragraph("(An Autonomous Institution)", subtitle_style))
    story.append(Paragraph("Coimbatore – 48", subtitle_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("FUNCTION REQUIREMENT FORM", title_style))
    story.append(Spacer(1, 10))

    # (iii) TRANSPORT
    story.append(Paragraph("<u><b>(iii) TRANSPORT</b></u>", sec_title_style))
    story.append(Spacer(1, 4))
    
    trans = get_related_attr(req, 'transport')
    trans_date = trans.date.strftime('%d-%m-%Y') if (trans and trans.required and trans.date) else ''
    trans_loc = f"{trans.pickup_location} -> {trans.drop_location}" if (trans and trans.required and trans.pickup_location) else ''
    trans_pick_time = trans.pickup_time.strftime('%I:%M %p') if (trans and trans.required and trans.pickup_time) else ''
    trans_drop_time = trans.drop_time.strftime('%I:%M %p') if (trans and trans.required and trans.drop_time) else ''
    trans_person = f"{trans.pickup_person_name} ({trans.pickup_person_contact})" if (trans and trans.required and trans.pickup_person_name) else ''
    
    trans_date_loc_data = [
        [
            Paragraph(trans_date, value_style),
            Paragraph("<b>Location:</b>", label_style),
            Paragraph(trans_loc, value_style)
        ]
    ]
    trans_date_loc_table = Table(trans_date_loc_data, colWidths=[80, 60, 163])
    trans_date_loc_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (0, 0), 0.5, colors.black),
        ('LINEBELOW', (2, 0), (2, 0), 0.5, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))

    trans_times_data = [
        [
            Paragraph(trans_pick_time, value_style),
            Paragraph("<b>Drop Time:</b>", label_style),
            Paragraph(trans_drop_time, value_style)
        ]
    ]
    trans_times_table = Table(trans_times_data, colWidths=[80, 80, 143])
    trans_times_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (0, 0), 0.5, colors.black),
        ('LINEBELOW', (2, 0), (2, 0), 0.5, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))

    trans_data = [
        [Paragraph("Transport Requirement Date :", label_style), trans_date_loc_table],
        [Paragraph("Pickup Time at NGPIT :", label_style), trans_times_table],
        [Paragraph("Name and Contact No. of the person to pick up the Guest :", label_style), Paragraph(trans_person, value_style)]
    ]
    trans_table = Table(trans_data, colWidths=[220, 303])
    trans_table.setStyle(TableStyle([
        ('LINEBELOW', (1, 2), (1, 2), 0.5, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))
    story.append(trans_table)
    story.append(Spacer(1, 10))
    
    # (iv) POWER / SYSTEM / CAMERA REQUIREMENT
    story.append(Paragraph("<u><b>(iv) POWER / SYSTEM / CAMERA REQUIREMENT</b></u>", sec_title_style))
    story.append(Spacer(1, 4))
    
    pc = get_related_attr(req, 'power_camera')
    
    mic_arr = "Yes [x]  No [ ]" if (pc and pc.mic_required) else "Yes [ ]  No [x]"
    mic_details = f"{pc.mic_type} (Qty: {pc.number_of_mics})" if (pc and pc.mic_required and pc.mic_type) else ''
    
    mic_type_data = [
        [
            Paragraph(mic_arr, value_style),
            Paragraph("<b>Type & No of Mic :</b>", label_style),
            Paragraph(mic_details, value_style)
        ]
    ]
    mic_type_table = Table(mic_type_data, colWidths=[90, 110, 103])
    mic_type_table.setStyle(TableStyle([
        ('LINEBELOW', (2, 0), (2, 0), 0.5, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))

    ac_arr = "Yes [x]  No [ ]" if (pc and pc.ac_required) else "Yes [ ]  No [x]"
    proj_arr = "Yes [x]  No [ ]" if (pc and pc.projector_required) else "Yes [ ]  No [x]"
    ac_proj_data = [
        [
            Paragraph(ac_arr, value_style),
            Paragraph("<b>LCD Projector :</b>", label_style),
            Paragraph(proj_arr, value_style)
        ]
    ]
    ac_proj_table = Table(ac_proj_data, colWidths=[90, 110, 103])
    ac_proj_table.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))

    photo_arr = "Yes [x]  No [ ]" if (pc and pc.photographer_required) else "Yes [ ]  No [x]"
    photo_type_str = "If Yes (Lab Technician [ ] / Official Photographer [ ])"
    if pc and pc.photographer_required and pc.photographer_type:
        if pc.photographer_type == 'LAB_TECHNICIAN':
            photo_type_str = "If Yes (Lab Technician [x] / Official Photographer [ ])"
        elif pc.photographer_type == 'OFFICIAL':
            photo_type_str = "If Yes (Lab Technician [ ] / Official Photographer [x])"
            
    photo_data = [
        [
            Paragraph(photo_arr, value_style),
            Paragraph(photo_type_str, label_style)
        ]
    ]
    photo_table = Table(photo_data, colWidths=[90, 213])
    photo_table.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))

    pc_data = [
        [Paragraph("Mic Arrangement", label_style), mic_type_table],
        [Paragraph("A/c Arrangement", label_style), ac_proj_table],
        [Paragraph("Laptop", label_style), Paragraph("Yes [x]  No [ ]" if (pc and pc.laptop_required) else "Yes [ ]  No [x]", value_style)],
        [Paragraph("Photograph Facility", label_style), photo_table]
    ]
    pc_table = Table(pc_data, colWidths=[220, 303])
    pc_table.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))
    story.append(pc_table)
    story.append(Spacer(1, 10))
    
    # (v) MEMENTO / SEATING / RECEPTION ITEM REQUIREMENT
    story.append(Paragraph("<u><b>(v) MEMENTO / SEATING / RECEPTION ITEM REQUIREMENT</b></u>", sec_title_style))
    story.append(Spacer(1, 4))
    
    mem = get_related_attr(req, 'memento')
    mem_required = "Yes [x]  No [ ]" if (mem and mem.required) else "Yes [ ]  No [x]"
    mem_worth = mem.honorarium_worth if (mem and mem.required and mem.honorarium_worth) else ''
    mem_qty = str(mem.quantity) if (mem and mem.required and mem.quantity) else ''
    
    mem_worth_data = [
        [
            Paragraph(mem_required, value_style),
            Paragraph("<b>(If Yes.) Worth of:</b>", label_style),
            Paragraph(mem_worth, value_style),
            Paragraph("<b>Quantity:</b>", label_style),
            Paragraph(mem_qty, value_style)
        ]
    ]
    mem_worth_table = Table(mem_worth_data, colWidths=[80, 80, 50, 60, 33])
    mem_worth_table.setStyle(TableStyle([
        ('LINEBELOW', (2, 0), (2, 0), 0.5, colors.black),
        ('LINEBELOW', (4, 0), (4, 0), 0.5, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))

    dias_seats = str(mem.dias_seats) if (mem and mem.dias_seats) else ''
    aud_seats = str(mem.audience_seats) if (mem and mem.audience_seats) else ''
    seating_data = [
        [
            Paragraph("a) Dias -", label_style), Paragraph(dias_seats, value_style),
            Paragraph("b) Audience -", label_style), Paragraph(aud_seats, value_style)
        ]
    ]
    seating_table = Table(seating_data, colWidths=[50, 80, 80, 93])
    seating_table.setStyle(TableStyle([
        ('LINEBELOW', (1, 0), (1, 0), 0.5, colors.black),
        ('LINEBELOW', (3, 0), (3, 0), 0.5, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))

    submitted_date = req.created_at.strftime('%d-%m-%Y %I:%M %p') if req.created_at else ''
    
    mem_data = [
        [Paragraph("Memento / Honorarium<br/>for Chief Guest", label_style), mem_worth_table],
        [Paragraph("No. of Seating Arrangements :", label_style), seating_table],
        [Paragraph("No. of Table Cloths", label_style), Paragraph(str(mem.table_cloths) if (mem and mem.table_cloths) else '', value_style)],
        [Paragraph("Reception Item Requirements:", label_style), Paragraph(mem.reception_items if (mem and mem.reception_items) else '', value_style)],
        [Paragraph("Function Form Submitted Date and Time", label_style), Paragraph(submitted_date, value_style)]
    ]
    
    mem_table = Table(mem_data, colWidths=[220, 303])
    mem_table.setStyle(TableStyle([
        ('LINEBELOW', (1, 2), (1, 4), 0.5, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))
    story.append(mem_table)
    story.append(Spacer(1, 15))
    
    # PREPARED BY / APPROVED BY BOX (Must remain blank for actual physical signatures)
    box_data = [
        [
            Paragraph("<b>PREPARED BY</b>", bold_label_style),
            Paragraph("<b>APPROVED BY</b>", bold_label_style),
            '',
            ''
        ],
        [
            Paragraph("Signature of the Staff", label_style),
            Paragraph("HOD", label_style),
            Paragraph("AO", label_style),
            Paragraph("Principal", label_style)
        ],
        ['', '', '', '']  # Height space for physical signing
    ]
    
    box_table = Table(box_data, colWidths=[140, 127, 127, 129], rowHeights=[20, 20, 45])
    box_table.setStyle(TableStyle([
        ('SPAN', (1, 0), (3, 0)),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(box_table)
    story.append(Spacer(1, 15))
    
    # Check List Section
    story.append(Paragraph("<u><b>Check List</b></u>", sec_title_style))
    story.append(Spacer(1, 6))
    
    chk_data = [
        [Paragraph("1. Principal Office", label_style), Paragraph(":", label_style), Paragraph("", value_style), Paragraph("6. Canteen (3 Copies)", label_style), Paragraph(":", label_style), Paragraph("", value_style)],
        [Paragraph("2. Madam Office", label_style), Paragraph(":", label_style), Paragraph("", value_style), Paragraph("7. Computer Cell", label_style), Paragraph(":", label_style), Paragraph("", value_style)],
        [Paragraph("3. Admin Office", label_style), Paragraph(":", label_style), Paragraph("", value_style), Paragraph("8. Electrical Department", label_style), Paragraph(":", label_style), Paragraph("", value_style)],
        [Paragraph("4. Memento Incharge", label_style), Paragraph(":", label_style), Paragraph("", value_style), Paragraph("9. Transport", label_style), Paragraph(":", label_style), Paragraph("", value_style)],
        [Paragraph("5. Stores", label_style), Paragraph(":", label_style), Paragraph("", value_style), Paragraph("10. House Keeping Supervisor", label_style), Paragraph(":", label_style), Paragraph("", value_style)]
    ]
    
    chk_table = Table(chk_data, colWidths=[150, 10, 91, 160, 10, 102])
    chk_table.setStyle(TableStyle([
        ('LINEBELOW', (2, 0), (2, -1), 0.5, colors.black),
        ('LINEBELOW', (5, 0), (5, -1), 0.5, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(chk_table)

    # Build the document
    doc.build(
        story,
        onFirstPage=draw_page_decorations,
        onLaterPages=draw_page_decorations
    )
    
    buffer.seek(0)
    return buffer
