from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class InspectionReport(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id"), unique=True, nullable=False)
    report_number = Column(String(100), unique=True, index=True, nullable=False)
    pdf_filename = Column(String(255), nullable=False)
    pdf_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    summary_data = Column(JSON, nullable=True)
    generated_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    inspection = relationship("Inspection", back_populates="report")
    generated_by = relationship("User")
