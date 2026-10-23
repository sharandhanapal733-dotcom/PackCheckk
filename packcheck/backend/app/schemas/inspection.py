from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel
from app.models.inspection import (
    InspectionStatus,
    CheckStatus,
    FieldStatus
)

class ProductInfo(BaseModel):
    name: str
    brand: Optional[str] = None
    category: Optional[str] = "Packaged Commodity"
    manufacturer: Optional[str] = None
    identifier: Optional[str] = None
    description: Optional[str] = None

class InspectionCreate(BaseModel):
    product_name: str
    brand: Optional[str] = None
    category: Optional[str] = "Packaged Food & Beverage"
    manufacturer: Optional[str] = None
    identifier: Optional[str] = None # Barcode or Batch
    location: Optional[str] = "Field Inspection Office"
    batch_number: Optional[str] = None
    inspector_remarks: Optional[str] = None

class FieldCorrectionRequest(BaseModel):
    corrected_value: str
    notes: Optional[str] = None

class DecisionRequest(BaseModel):
    status: InspectionStatus
    notes: Optional[str] = None

class OCRItemResponse(BaseModel):
    id: Optional[int] = None
    text: str
    confidence: float
    box: List[int]
    line_number: int
    engine: str

class InspectionImageResponse(BaseModel):
    id: int
    file_path: str
    original_filename: str
    preprocessed_path: Optional[str] = None
    image_side: str
    width: Optional[int] = None
    height: Optional[int] = None
    ocr_results: List[OCRItemResponse] = []

    class Config:
        from_attributes = True

class ExtractedFieldResponse(BaseModel):
    id: int
    field_name: str
    field_value: Optional[str] = None
    unit: Optional[str] = None
    currency: Optional[str] = None
    confidence: float
    status: FieldStatus
    original_ocr_text: Optional[str] = None
    bbox: Optional[Any] = None
    image_id: Optional[int] = None
    is_manually_corrected: bool = False
    corrected_value: Optional[str] = None
    correction_notes: Optional[str] = None
    corrected_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ComplianceResultResponse(BaseModel):
    id: int
    rule_id: str
    field_name: str
    status: CheckStatus
    severity: str
    message: str
    legal_reference: str
    evidence: Optional[Any] = None

    class Config:
        from_attributes = True

class ViolationResponse(BaseModel):
    id: int
    field_name: str
    violation_type: str
    severity: str
    description: str
    evidence_text: Optional[str] = None
    legal_reference: str
    recommended_action: Optional[str] = None
    status: str

    class Config:
        from_attributes = True

class ProductResponse(BaseModel):
    id: int
    name: str
    brand: Optional[str] = None
    category: str
    manufacturer: Optional[str] = None
    identifier: Optional[str] = None

    class Config:
        from_attributes = True

class InspectionSummaryResponse(BaseModel):
    id: int
    inspection_number: str
    product: ProductResponse
    inspector_name: str
    inspection_date: datetime
    location: Optional[str] = None
    overall_status: InspectionStatus
    compliance_score: float
    total_checks: int
    passed_checks: int
    violations_count: int
    manual_review_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class InspectionDetailResponse(InspectionSummaryResponse):
    batch_number: Optional[str] = None
    inspector_remarks: Optional[str] = None
    images: List[InspectionImageResponse] = []
    extracted_fields: List[ExtractedFieldResponse] = []
    compliance_results: List[ComplianceResultResponse] = []
    violations: List[ViolationResponse] = []
    has_report: bool = False
    report_id: Optional[int] = None
