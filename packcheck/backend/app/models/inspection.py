import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class InspectionStatus(str, enum.Enum):
    COMPLIANT = "COMPLIANT"
    POTENTIAL_NON_COMPLIANCE = "POTENTIAL_NON_COMPLIANCE"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"

class CheckStatus(str, enum.Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    NOT_DETECTED = "NOT_DETECTED"

class FieldStatus(str, enum.Enum):
    DETECTED = "DETECTED"
    NOT_DETECTED = "NOT_DETECTED"
    MANUAL_CORRECTED = "MANUAL_CORRECTED"

class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)
    inspection_number = Column(String(50), unique=True, index=True, nullable=False) # e.g. PC-2026-0001
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    inspection_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    location = Column(String(255), nullable=True, default="Field Inspection Station")
    batch_number = Column(String(100), nullable=True)
    inspector_remarks = Column(Text, nullable=True)
    
    overall_status = Column(Enum(InspectionStatus), default=InspectionStatus.MANUAL_REVIEW_REQUIRED, nullable=False)
    compliance_score = Column(Float, default=0.0) # Transparent calculation
    total_checks = Column(Integer, default=0)
    passed_checks = Column(Integer, default=0)
    violations_count = Column(Integer, default=0)
    manual_review_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="inspections")
    inspector = relationship("User", back_populates="inspections")
    images = relationship("InspectionImage", back_populates="inspection", cascade="all, delete-orphan")
    extracted_fields = relationship("ExtractedField", back_populates="inspection", cascade="all, delete-orphan")
    compliance_results = relationship("ComplianceResult", back_populates="inspection", cascade="all, delete-orphan")
    violations = relationship("Violation", back_populates="inspection", cascade="all, delete-orphan")
    report = relationship("InspectionReport", back_populates="inspection", uselist=False, cascade="all, delete-orphan")

class InspectionImage(Base):
    __tablename__ = "inspection_images"

    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=False)
    preprocessed_path = Column(String(500), nullable=True)
    image_side = Column(String(50), default="Front/Package Side") # Front, Back, Side, Nutritional/Declaration panel
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    inspection = relationship("Inspection", back_populates="images")
    ocr_results = relationship("OCRResult", back_populates="image", cascade="all, delete-orphan")

class OCRResult(Base):
    __tablename__ = "ocr_results"

    id = Column(Integer, primary_key=True, index=True)
    inspection_image_id = Column(Integer, ForeignKey("inspection_images.id"), nullable=False)
    text = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    bbox = Column(JSON, nullable=False) # e.g. [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    line_number = Column(Integer, default=0)
    engine = Column(String(50), default="RapidOCR (PaddleOCR-v4)")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    image = relationship("InspectionImage", back_populates="ocr_results")

class ExtractedField(Base):
    __tablename__ = "extracted_fields"

    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id"), nullable=False)
    field_name = Column(String(100), index=True, nullable=False) # manufacturer, net_quantity, mrp, date, consumer_care, country_of_origin
    field_value = Column(Text, nullable=True)
    unit = Column(String(50), nullable=True) # g, kg, ml, l, N, U
    currency = Column(String(20), nullable=True) # INR / Rs / ₹
    confidence = Column(Float, default=0.0)
    status = Column(Enum(FieldStatus), default=FieldStatus.DETECTED, nullable=False)
    original_ocr_text = Column(Text, nullable=True)
    bbox = Column(JSON, nullable=True) # Bounding box evidence
    image_id = Column(Integer, nullable=True) # ID of image where detected
    
    # Manual correction audit
    is_manually_corrected = Column(Boolean, default=False)
    corrected_value = Column(Text, nullable=True)
    corrected_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    corrected_at = Column(DateTime, nullable=True)
    correction_notes = Column(Text, nullable=True)

    # Relationships
    inspection = relationship("Inspection", back_populates="extracted_fields")
    corrected_by = relationship("User", foreign_keys=[corrected_by_id])

class ComplianceResult(Base):
    __tablename__ = "compliance_results"

    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id"), nullable=False)
    rule_id = Column(String(50), nullable=False)
    field_name = Column(String(100), nullable=False)
    status = Column(Enum(CheckStatus), nullable=False)
    severity = Column(String(50), default="HIGH")
    message = Column(Text, nullable=False)
    legal_reference = Column(String(255), nullable=False)
    evidence = Column(JSON, nullable=True) # text, bbox, confidence
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    inspection = relationship("Inspection", back_populates="compliance_results")

class Violation(Base):
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id"), nullable=False)
    field_name = Column(String(100), nullable=False)
    violation_type = Column(String(100), nullable=False) # MISSING_DECLARATION, INVALID_FORMAT, LOW_OCR_CONFIDENCE, READABILITY_ISSUE, FONT_SIZE_REVIEW
    severity = Column(String(50), default="HIGH") # CRITICAL, HIGH, MEDIUM, LOW
    description = Column(Text, nullable=False)
    evidence_text = Column(Text, nullable=True)
    legal_reference = Column(String(255), nullable=False)
    recommended_action = Column(Text, nullable=True)
    status = Column(String(50), default="ACTIVE") # ACTIVE, RESOLVED, WAIVED
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    inspection = relationship("Inspection", back_populates="violations")
