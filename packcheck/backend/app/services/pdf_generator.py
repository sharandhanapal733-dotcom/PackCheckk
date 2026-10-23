import os
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.config import settings

def generate_pdf_report(inspection, db_session) -> str:
    """
    Generates a professional inspection report PDF using ReportLab.
    Saves the PDF to settings.REPORT_DIR and returns the file path.
    """
    report_filename = f"Report_{inspection.inspection_number}.pdf"
    report_path = str(settings.REPORT_DIR / report_filename)

    doc = SimpleDocTemplate(
        report_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom typography
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748b'),
    )
    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155'),
    )
    body_bold = ParagraphStyle(
        'BodyBold',
        parent=body_style,
        fontName='Helvetica-Bold',
    )

    story = []

    # 1. Header Banner
    header_data = [
        [
            Paragraph("<b>PACKCHECK</b><br/><font size=8 color='#64748b'>Legal Metrology Compliance System</font>", title_style),
            Paragraph(f"<b>INSPECTION REPORT</b><br/><font size=9 color='#2563eb'><b>ID: {inspection.inspection_number}</b></font><br/><font size=8 color='#64748b'>Date: {inspection.inspection_date.strftime('%d-%b-%Y %H:%M')}</font>", ParagraphStyle('HRight', parent=styles['Normal'], alignment=2))
        ]
    ]
    header_table = Table(header_data, colWidths=[3.5 * inch, 4.0 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#cbd5e1'), spaceBefore=2, spaceAfter=12))

    # 2. Executive Status Callout
    status_str = inspection.overall_status.value if hasattr(inspection.overall_status, "value") else str(inspection.overall_status)
    if "COMPLIANT" in status_str and "NON" not in status_str:
        status_bg = colors.HexColor('#ecfdf5')
        status_border = colors.HexColor('#059669')
        status_text = "<font color='#059669'><b>STATUS: COMPLIANT WITH LEGAL METROLOGY (PC) RULES, 2011</b></font>"
    elif "POTENTIAL" in status_str or "NON" in status_str:
        status_bg = colors.HexColor('#fef2f2')
        status_border = colors.HexColor('#dc2626')
        status_text = "<font color='#dc2626'><b>STATUS: POTENTIAL NON-COMPLIANCE DETECTED (ACTION RECOMMENDED)</b></font>"
    else:
        status_bg = colors.HexColor('#fffbeb')
        status_border = colors.HexColor('#d97706')
        status_text = "<font color='#d97706'><b>STATUS: MANUAL REVIEW REQUIRED BY ENFORCEMENT OFFICER</b></font>"

    status_data = [[
        Paragraph(f"{status_text}<br/><font size=8 color='#475569'>Compliance Score: <b>{inspection.compliance_score}%</b> | Applicable Checks: {inspection.total_checks} | Passed: {inspection.passed_checks} | Flagged Issues: {inspection.violations_count}</font>", body_style)
    ]]
    status_table = Table(status_data, colWidths=[7.5 * inch])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), status_bg),
        ('BOX', (0,0), (-1,-1), 1, status_border),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(status_table)
    story.append(Spacer(1, 12))

    # 3. Product & Inspection Details
    prod = inspection.product
    inspector = inspection.inspector
    meta_data = [
        [Paragraph("<b>Product Name:</b>", body_bold), Paragraph(prod.name if prod else "N/A", body_style),
         Paragraph("<b>Inspector:</b>", body_bold), Paragraph(inspector.full_name if inspector else "N/A", body_style)],
        [Paragraph("<b>Brand / Trademark:</b>", body_bold), Paragraph(prod.brand or "N/A", body_style),
         Paragraph("<b>Badge Number:</b>", body_bold), Paragraph(inspector.badge_number or "N/A", body_style)],
        [Paragraph("<b>Category:</b>", body_bold), Paragraph(prod.category or "Packaged Commodity", body_style),
         Paragraph("<b>Inspection Location:</b>", body_bold), Paragraph(inspection.location or "Field", body_style)],
        [Paragraph("<b>Batch / Identifier:</b>", body_bold), Paragraph(inspection.batch_number or prod.identifier or "N/A", body_style),
         Paragraph("<b>Department:</b>", body_bold), Paragraph("Legal Metrology Enforcement", body_style)],
    ]
    meta_table = Table(meta_data, colWidths=[1.5 * inch, 2.25 * inch, 1.5 * inch, 2.25 * inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # 4. Mandatory Declarations Table
    story.append(Paragraph("Mandatory Declarations Assessment (Rule 6, LMPC Rules 2011)", h2_style))
    decl_headers = [
        Paragraph("<b>Declaration Field</b>", body_bold),
        Paragraph("<b>Extracted Value</b>", body_bold),
        Paragraph("<b>OCR Text Evidence</b>", body_bold),
        Paragraph("<b>Confidence</b>", body_bold),
        Paragraph("<b>Status</b>", body_bold),
    ]
    decl_rows = [decl_headers]

    for f in inspection.extracted_fields:
        stat_color = '#059669' if f.status.value == "DETECTED" and f.confidence >= 0.65 else '#d97706' if f.status.value == "DETECTED" else '#dc2626'
        status_disp = f.status.value if hasattr(f.status, "value") else str(f.status)
        if f.is_manually_corrected:
            status_disp += " (Corrected)"
            stat_color = '#2563eb'

        decl_rows.append([
            Paragraph(f.field_name.replace('_', ' ').title(), body_bold),
            Paragraph(str(f.corrected_value or f.field_value or "Not Detected"), body_style),
            Paragraph(str(f.original_ocr_text or "—")[:80], body_style),
            Paragraph(f"{int(f.confidence * 100)}%", body_style),
            Paragraph(f"<font color='{stat_color}'><b>{status_disp}</b></font>", body_style),
        ])

    decl_table = Table(decl_rows, colWidths=[1.6 * inch, 1.8 * inch, 2.4 * inch, 0.8 * inch, 0.9 * inch])
    decl_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(decl_table)
    story.append(Spacer(1, 14))

    # 5. Flagged Violations & Observations
    if inspection.violations:
        story.append(Paragraph(f"Flagged Observations & Violations ({len(inspection.violations)})", h2_style))
        viol_headers = [
            Paragraph("<b>Severity</b>", body_bold),
            Paragraph("<b>Rule Reference</b>", body_bold),
            Paragraph("<b>Description & Observation</b>", body_bold),
            Paragraph("<b>Recommended Action</b>", body_bold),
        ]
        viol_rows = [viol_headers]
        for v in inspection.violations:
            sev_color = '#dc2626' if v.severity == "CRITICAL" or v.severity == "HIGH" else '#d97706'
            viol_rows.append([
                Paragraph(f"<font color='{sev_color}'><b>{v.severity}</b></font>", body_style),
                Paragraph(v.legal_reference or "LMPC 2011", body_style),
                Paragraph(v.description, body_style),
                Paragraph(v.recommended_action or "Manual verification required.", body_style),
            ])
        viol_table = Table(viol_rows, colWidths=[0.9 * inch, 2.0 * inch, 2.6 * inch, 2.0 * inch])
        viol_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#fef2f2')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#fca5a5')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#fee2e2')),
            ('PADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(viol_table)
        story.append(Spacer(1, 14))

    # 6. Remarks & Evidence Images
    if inspection.inspector_remarks:
        story.append(Paragraph(f"<b>Inspector Remarks:</b> {inspection.inspector_remarks}", body_style))
        story.append(Spacer(1, 10))

    # Attach evidence images if available and file exists
    image_flowables = []
    for img in inspection.images[:2]:
        p = Path(img.file_path)
        if not p.is_absolute():
            p = settings.UPLOAD_DIR / p.name
        if p.exists():
            try:
                # Add image scaled to max width 3.2 inch
                rl_img = RLImage(str(p), width=3.2 * inch, height=2.4 * inch)
                image_flowables.append(rl_img)
            except Exception:
                pass

    if image_flowables:
        story.append(Paragraph("Attached Photographic Evidence", h2_style))
        img_table = Table([image_flowables], colWidths=[3.7 * inch] * len(image_flowables))
        img_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(img_table)
        story.append(Spacer(1, 14))

    # 7. Legal Disclaimer and Official Attestation
    disclaimer_text = (
        "<b>LEGAL NOTICE & SYSTEM ATTESTATION:</b> This report represents an automated preliminary screening assessment "
        "conducted under the Legal Metrology (Packaged Commodities) Rules, 2011 using the PackCheck automated vision & OCR system. "
        "In accordance with official guidelines, automated detections are advisory; final determination of compliance and any statutory "
        "proceedings rest exclusively with the designated Inspector of Legal Metrology upon physical verification."
    )
    story.append(KeepTogether([
        HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceBefore=10, spaceAfter=8),
        Paragraph(disclaimer_text, ParagraphStyle('Disc', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=7.5, leading=10, textColor=colors.HexColor('#64748b'))),
        Spacer(1, 12),
        Table([
            [
                Paragraph("<b>Generated by PackCheck Engine</b><br/>Govt. Compliance Verification Suite", body_style),
                Paragraph("<b>Verified By Inspector:</b><br/>___________________________<br/>(Signature & Seal)", ParagraphStyle('Sig', parent=styles['Normal'], alignment=2))
            ]
        ], colWidths=[3.75 * inch, 3.75 * inch])
    ]))

    doc.build(story)
    return report_path
