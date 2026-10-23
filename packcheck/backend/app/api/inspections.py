import os
import shutil
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.rule import ComplianceRule
from app.models.inspection import (
    Inspection,
    InspectionImage,
    OCRResult,
    ExtractedField,
    ComplianceResult,
    Violation,
    InspectionStatus,
    CheckStatus,
    FieldStatus,
)
from app.models.audit import AuditLog
from app.schemas.inspection import (
    InspectionCreate,
    InspectionSummaryResponse,
    InspectionDetailResponse,
    FieldCorrectionRequest,
    DecisionRequest,
    ExtractedFieldResponse,
)
from app.services.auth_service import get_current_user
from app.services.preprocessing import preprocess_image, get_image_dimensions
from app.services.ocr_engine import run_ocr
from app.services.extraction import FieldExtractor
from app.services.compliance_engine import ComplianceEngine

router = APIRouter(prefix="/api/inspections", tags=["Inspections"])

def generate_inspection_number(db: Session) -> str:
    count = db.query(Inspection).count() + 1
    year = datetime.utcnow().year
    return f"PC-{year}-{count:04d}"

@router.post("", response_model=InspectionDetailResponse, status_code=status.HTTP_201_CREATED)
def create_inspection(
    data: InspectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Find or create product
    product = None
    if data.identifier:
        product = db.query(Product).filter(Product.identifier == data.identifier).first()
    if not product:
        product = db.query(Product).filter(
            Product.name == data.product_name,
            Product.brand == data.brand
        ).first()

    if not product:
        product = Product(
            name=data.product_name,
            brand=data.brand,
            category=data.category or "Packaged Commodity",
            manufacturer=data.manufacturer,
            identifier=data.identifier,
        )
        db.add(product)
        db.flush()

    inspection = Inspection(
        inspection_number=generate_inspection_number(db),
        product_id=product.id,
        inspector_id=current_user.id,
        location=data.location or "Enforcement Inspection Office",
        batch_number=data.batch_number,
        inspector_remarks=data.inspector_remarks,
        overall_status=InspectionStatus.MANUAL_REVIEW_REQUIRED,
        compliance_score=0.0,
    )
    db.add(inspection)
    db.commit()
    db.refresh(inspection)

    # Log action
    audit = AuditLog(
        user_id=current_user.id,
        action="CREATE_INSPECTION",
        entity_type="Inspection",
        entity_id=str(inspection.id),
        details={"inspection_number": inspection.inspection_number, "product": product.name}
    )
    db.add(audit)
    db.commit()

    return format_inspection_detail(inspection)

@router.get("", response_model=List[InspectionSummaryResponse])
def list_inspections(
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Inspection).join(Product).join(User, Inspection.inspector_id == User.id)

    if status_filter:
        query = query.filter(Inspection.overall_status == status_filter)

    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (Inspection.inspection_number.ilike(search_fmt)) |
            (Product.name.ilike(search_fmt)) |
            (Product.brand.ilike(search_fmt)) |
            (User.full_name.ilike(search_fmt))
        )

    # If inspector, allow viewing all or own inspections
    inspections = query.order_by(desc(Inspection.inspection_date)).offset(offset).limit(limit).all()

    results = []
    for insp in inspections:
        results.append(format_inspection_summary(insp))
    return results

@router.get("/{id}", response_model=InspectionDetailResponse)
def get_inspection(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inspection = db.query(Inspection).filter(Inspection.id == id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection record not found")
    return format_inspection_detail(inspection)

@router.post("/{id}/images")
async def upload_inspection_images(
    id: int,
    files: List[UploadFile] = File(...),
    image_side: str = Form("Package Side"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inspection = db.query(Inspection).filter(Inspection.id == id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")

    saved_images = []
    allowed_types = {"image/jpeg", "image/jpg", "image/png", "image/webp"}

    for file in files:
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image type: {file.content_type}. Please upload JPG, JPEG, PNG, or WEBP."
            )

        ext = os.path.splitext(file.filename)[1].lower() or ".jpg"
        unique_name = f"{inspection.inspection_number}_{uuid.uuid4().hex[:8]}{ext}"
        destination = settings.UPLOAD_DIR / unique_name

        with open(destination, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Get original dimensions
        w, h = get_image_dimensions(str(destination))

        img_record = InspectionImage(
            inspection_id=inspection.id,
            file_path=f"uploads/{unique_name}",
            original_filename=file.filename,
            image_side=image_side,
            width=w,
            height=h
        )
        db.add(img_record)
        saved_images.append(img_record)

    db.commit()
    for s in saved_images:
        db.refresh(s)

    return {
        "message": f"Successfully uploaded {len(saved_images)} image(s)",
        "images": [{"id": img.id, "file_path": img.file_path, "original_filename": img.original_filename} for img in saved_images]
    }

@router.post("/{id}/process", response_model=InspectionDetailResponse)
def process_inspection(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Executes the full automated compliance pipeline:
    1. Preprocessing images
    2. PaddleOCR text & bounding boxes extraction
    3. Structured LMPC declaration extraction
    4. Legal Metrology rule validation engine
    5. Scoring & violation detection
    6. Database persistence
    """
    inspection = db.query(Inspection).filter(Inspection.id == id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")

    if not inspection.images:
        raise HTTPException(status_code=400, detail="No package images uploaded yet for this inspection.")

    # Clear previous processing results for clean re-processing
    db.query(OCRResult).filter(OCRResult.inspection_image_id.in_([img.id for img in inspection.images])).delete(synchronize_session=False)
    db.query(ExtractedField).filter(ExtractedField.inspection_id == id).delete(synchronize_session=False)
    db.query(ComplianceResult).filter(ComplianceResult.inspection_id == id).delete(synchronize_session=False)
    db.query(Violation).filter(Violation.inspection_id == id).delete(synchronize_session=False)
    db.commit()

    all_ocr_results = []

    # 1 & 2: Preprocess and Run OCR on each image
    for img_rec in inspection.images:
        orig_full_path = settings.BASE_DIR / img_rec.file_path
        if not orig_full_path.exists():
            continue

        # Preprocess
        prep_name = f"prep_{os.path.basename(orig_full_path)}"
        prep_path = str(settings.UPLOAD_DIR / prep_name)
        try:
            preprocess_image(str(orig_full_path), prep_path)
            img_rec.preprocessed_path = f"uploads/{prep_name}"
        except Exception:
            prep_path = str(orig_full_path)

        # Run OCR
        try:
            ocr_lines = run_ocr(prep_path)
        except Exception as e:
            ocr_lines = []

        # Store OCR Results
        for line in ocr_lines:
            ocr_item = OCRResult(
                inspection_image_id=img_rec.id,
                text=line["text"],
                confidence=line["confidence"],
                bbox=line["box"],
                line_number=line["line_number"],
                engine=line["engine"]
            )
            db.add(ocr_item)
            # Annotate with image id for field tracking
            line_copy = dict(line)
            line_copy["image_id"] = img_rec.id
            all_ocr_results.append(line_copy)

    db.commit()

    # 3: Extract structured fields
    extracted_data = FieldExtractor.extract_all(all_ocr_results)

    # Save Extracted Fields into DB
    for f_name, f_data in extracted_data.items():
        field_rec = ExtractedField(
            inspection_id=inspection.id,
            field_name=f_name,
            field_value=str(f_data.get("value") or ""),
            unit=f_data.get("unit"),
            currency=f_data.get("currency"),
            confidence=f_data.get("confidence", 0.0),
            status=FieldStatus.DETECTED if f_data.get("status") == "DETECTED" else FieldStatus.NOT_DETECTED,
            original_ocr_text=f_data.get("original_ocr_text"),
            bbox=f_data.get("bbox"),
            image_id=f_data.get("image_id"),
        )
        db.add(field_rec)

    db.commit()

    # 4: Rule Engine Evaluation
    rules = db.query(ComplianceRule).filter(ComplianceRule.enabled == True).all()
    eval_output = ComplianceEngine.evaluate(extracted_data, rules, all_ocr_results)

    # Save Compliance Results
    for cr in eval_output["results"]:
        c_res = ComplianceResult(
            inspection_id=inspection.id,
            rule_id=cr["rule_id"],
            field_name=cr["field_name"],
            status=cr["status"],
            severity=cr["severity"],
            message=cr["message"],
            legal_reference=cr["legal_reference"],
            evidence=cr["evidence"]
        )
        db.add(c_res)

    # Save Violations
    for v in eval_output["violations"]:
        viol = Violation(
            inspection_id=inspection.id,
            field_name=v["field_name"],
            violation_type=v["violation_type"],
            severity=v["severity"],
            description=v["description"],
            evidence_text=v["evidence_text"],
            legal_reference=v["legal_reference"],
            recommended_action=v["recommended_action"],
            status="ACTIVE"
        )
        db.add(viol)

    # Update Inspection Header
    inspection.overall_status = eval_output["overall_status"]
    inspection.compliance_score = eval_output["compliance_score"]
    inspection.total_checks = eval_output["total_checks"]
    inspection.passed_checks = eval_output["passed_checks"]
    inspection.violations_count = eval_output["violations_count"]
    inspection.manual_review_count = eval_output["manual_review_count"]
    inspection.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(inspection)

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="PROCESS_INSPECTION",
        entity_type="Inspection",
        entity_id=str(inspection.id),
        details={
            "score": inspection.compliance_score,
            "status": inspection.overall_status.value,
            "violations": inspection.violations_count
        }
    )
    db.add(audit)
    db.commit()

    return format_inspection_detail(inspection)

@router.patch("/{id}/fields/{field_id}", response_model=ExtractedFieldResponse)
def correct_extracted_field(
    id: int,
    field_id: int,
    body: FieldCorrectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Allows enforcement officers to correct OCR misreadings while preserving original evidence.
    """
    field_rec = db.query(ExtractedField).filter(
        ExtractedField.id == field_id,
        ExtractedField.inspection_id == id
    ).first()

    if not field_rec:
        raise HTTPException(status_code=404, detail="Extracted field not found")

    old_val = field_rec.corrected_value or field_rec.field_value
    field_rec.is_manually_corrected = True
    field_rec.corrected_value = body.corrected_value
    field_rec.correction_notes = body.notes
    field_rec.corrected_by_id = current_user.id
    field_rec.corrected_at = datetime.utcnow()
    field_rec.status = FieldStatus.MANUAL_CORRECTED

    # Log manual correction
    audit = AuditLog(
        user_id=current_user.id,
        action="MANUAL_CORRECTION",
        entity_type="ExtractedField",
        entity_id=str(field_rec.id),
        details={
            "inspection_id": id,
            "field": field_rec.field_name,
            "old_value": old_val,
            "new_value": body.corrected_value
        }
    )
    db.add(audit)
    db.commit()
    db.refresh(field_rec)

    # Re-evaluate compliance dynamically with the corrected field
    re_evaluate_inspection(id, db)

    return field_rec

def re_evaluate_inspection(inspection_id: int, db: Session):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        return

    # Build fields dict from current database fields
    fields_dict = {}
    for f in inspection.extracted_fields:
        effective_val = f.corrected_value if f.is_manually_corrected else f.field_value
        fields_dict[f.field_name] = {
            "status": "DETECTED" if effective_val else "NOT_DETECTED",
            "value": effective_val,
            "unit": f.unit,
            "currency": f.currency,
            "confidence": 1.0 if f.is_manually_corrected else f.confidence,
            "original_ocr_text": f.original_ocr_text,
            "bbox": f.bbox,
        }

    rules = db.query(ComplianceRule).filter(ComplianceRule.enabled == True).all()
    eval_output = ComplianceEngine.evaluate(fields_dict, rules, [])

    # Update inspection record
    inspection.overall_status = eval_output["overall_status"]
    inspection.compliance_score = eval_output["compliance_score"]
    inspection.total_checks = eval_output["total_checks"]
    inspection.passed_checks = eval_output["passed_checks"]
    inspection.violations_count = eval_output["violations_count"]
    inspection.manual_review_count = eval_output["manual_review_count"]
    db.commit()

@router.post("/{id}/decision", response_model=InspectionDetailResponse)
def record_officer_decision(
    id: int,
    body: DecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Enforcement officer records final statutory decision and remarks for the inspection.
    """
    inspection = db.query(Inspection).filter(Inspection.id == id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")

    inspection.overall_status = body.status
    if body.notes:
        inspection.inspector_remarks = f"{inspection.inspector_remarks or ''}\n[Officer Decision]: {body.notes}".strip()
    inspection.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(inspection)

    # Log audit
    audit = AuditLog(
        user_id=current_user.id,
        action="RECORD_DECISION",
        entity_type="Inspection",
        entity_id=str(inspection.id),
        details={"status": body.status.value, "notes": body.notes}
    )
    db.add(audit)
    db.commit()

    return format_inspection_detail(inspection)

@router.get("/{id}/ocr")
def get_inspection_ocr(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inspection = db.query(Inspection).filter(Inspection.id == id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")

    items = []
    for img in inspection.images:
        for r in img.ocr_results:
            items.append({
                "id": r.id,
                "image_id": img.id,
                "image_path": img.file_path,
                "text": r.text,
                "confidence": r.confidence,
                "box": r.bbox,
                "line_number": r.line_number,
                "engine": r.engine
            })
    return items

@router.get("/{id}/fields")
def get_inspection_fields(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inspection = db.query(Inspection).filter(Inspection.id == id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return inspection.extracted_fields

@router.get("/{id}/compliance")
def get_inspection_compliance(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inspection = db.query(Inspection).filter(Inspection.id == id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return {
        "overall_status": inspection.overall_status,
        "compliance_score": inspection.compliance_score,
        "total_checks": inspection.total_checks,
        "passed_checks": inspection.passed_checks,
        "results": inspection.compliance_results,
        "violations": inspection.violations
    }

# Helper formatters
def format_inspection_summary(insp: Inspection) -> dict:
    return {
        "id": insp.id,
        "inspection_number": insp.inspection_number,
        "product": {
            "id": insp.product.id,
            "name": insp.product.name,
            "brand": insp.product.brand,
            "category": insp.product.category,
            "manufacturer": insp.product.manufacturer,
            "identifier": insp.product.identifier,
        },
        "inspector_name": insp.inspector.full_name if insp.inspector else "Officer",
        "inspection_date": insp.inspection_date,
        "location": insp.location,
        "overall_status": insp.overall_status,
        "compliance_score": insp.compliance_score,
        "total_checks": insp.total_checks,
        "passed_checks": insp.passed_checks,
        "violations_count": insp.violations_count,
        "manual_review_count": insp.manual_review_count,
        "created_at": insp.created_at,
    }

def format_inspection_detail(insp: Inspection) -> dict:
    summary = format_inspection_summary(insp)
    
    images_data = []
    for img in insp.images:
        images_data.append({
            "id": img.id,
            "file_path": img.file_path,
            "original_filename": img.original_filename,
            "preprocessed_path": img.preprocessed_path,
            "image_side": img.image_side,
            "width": img.width,
            "height": img.height,
            "ocr_results": [
                {
                    "id": o.id,
                    "text": o.text,
                    "confidence": o.confidence,
                    "box": o.bbox,
                    "line_number": o.line_number,
                    "engine": o.engine
                } for o in img.ocr_results
            ]
        })

    fields_data = [
        {
            "id": f.id,
            "field_name": f.field_name,
            "field_value": f.field_value,
            "unit": f.unit,
            "currency": f.currency,
            "confidence": f.confidence,
            "status": f.status,
            "original_ocr_text": f.original_ocr_text,
            "bbox": f.bbox,
            "image_id": f.image_id,
            "is_manually_corrected": f.is_manually_corrected,
            "corrected_value": f.corrected_value,
            "correction_notes": f.correction_notes,
            "corrected_at": f.corrected_at,
        } for f in insp.extracted_fields
    ]

    comp_results = [
        {
            "id": c.id,
            "rule_id": c.rule_id,
            "field_name": c.field_name,
            "status": c.status,
            "severity": c.severity,
            "message": c.message,
            "legal_reference": c.legal_reference,
            "evidence": c.evidence,
        } for c in insp.compliance_results
    ]

    violations_data = [
        {
            "id": v.id,
            "field_name": v.field_name,
            "violation_type": v.violation_type,
            "severity": v.severity,
            "description": v.description,
            "evidence_text": v.evidence_text,
            "legal_reference": v.legal_reference,
            "recommended_action": v.recommended_action,
            "status": v.status,
        } for v in insp.violations
    ]

    summary.update({
        "batch_number": insp.batch_number,
        "inspector_remarks": insp.inspector_remarks,
        "images": images_data,
        "extracted_fields": fields_data,
        "compliance_results": comp_results,
        "violations": violations_data,
        "has_report": insp.report is not None,
        "report_id": insp.report.id if insp.report else None,
    })
    return summary
