import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.inspection import Inspection
from app.models.report import InspectionReport
from app.models.audit import AuditLog
from app.services.auth_service import get_current_user, get_current_user_optional
from app.services.pdf_generator import generate_pdf_report

router = APIRouter(prefix="/api/reports", tags=["Inspection Reports"])

@router.post("/{inspection_id}/generate")
def create_or_regenerate_report(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")

    pdf_path = generate_pdf_report(inspection, db)
    file_size = os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0

    report = db.query(InspectionReport).filter(InspectionReport.inspection_id == inspection_id).first()
    if not report:
        report = InspectionReport(
            inspection_id=inspection.id,
            report_number=f"REP-{inspection.inspection_number}",
            pdf_filename=os.path.basename(pdf_path),
            pdf_path=pdf_path,
            file_size_bytes=file_size,
            generated_by_id=current_user.id,
        )
        db.add(report)
    else:
        report.pdf_filename = os.path.basename(pdf_path)
        report.pdf_path = pdf_path
        report.file_size_bytes = file_size
        report.generated_by_id = current_user.id

    db.commit()
    db.refresh(report)

    # Log action
    audit = AuditLog(
        user_id=current_user.id,
        action="GENERATE_REPORT",
        entity_type="Report",
        entity_id=str(report.id),
        details={"inspection_id": inspection_id, "report_number": report.report_number}
    )
    db.add(audit)
    db.commit()

    return {
        "message": "PDF report generated successfully",
        "report_id": report.id,
        "report_number": report.report_number,
        "pdf_filename": report.pdf_filename,
        "download_url": f"/api/reports/{report.id}/download"
    }

@router.get("/{id}/download")
def download_report(
    id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    report = db.query(InspectionReport).filter(InspectionReport.id == id).first()
    if not report or not os.path.exists(report.pdf_path):
        raise HTTPException(status_code=404, detail="Report file not found")

    return FileResponse(
        path=report.pdf_path,
        media_type="application/pdf",
        filename=report.pdf_filename,
        headers={"Content-Disposition": f"inline; filename=\"{report.pdf_filename}\""}
    )

@router.get("/inspection/{inspection_id}/pdf")
def download_report_by_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    report = db.query(InspectionReport).filter(InspectionReport.inspection_id == inspection_id).first()
    if not report or not os.path.exists(report.pdf_path):
        # Auto generate if not exists
        inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
        if not inspection:
            raise HTTPException(status_code=404, detail="Inspection not found")
        pdf_path = generate_pdf_report(inspection, db)
        file_size = os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0
        gen_user_id = current_user.id if current_user else inspection.inspector_id
        report = InspectionReport(
            inspection_id=inspection.id,
            report_number=f"REP-{inspection.inspection_number}",
            pdf_filename=os.path.basename(pdf_path),
            pdf_path=pdf_path,
            file_size_bytes=file_size,
            generated_by_id=gen_user_id,
        )
        db.add(report)
        db.commit()
        db.refresh(report)

    return FileResponse(
        path=report.pdf_path,
        media_type="application/pdf",
        filename=report.pdf_filename,
        headers={"Content-Disposition": f"inline; filename=\"{report.pdf_filename}\""}
    )
