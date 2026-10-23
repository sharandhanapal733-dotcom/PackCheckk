from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    brand = Column(String(255), index=True, nullable=True)
    category = Column(String(100), index=True, nullable=False, default="Food & Beverages")
    manufacturer = Column(String(255), nullable=True)
    identifier = Column(String(100), index=True, nullable=True)  # Barcode, EAN, or Batch ID
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    inspections = relationship("Inspection", back_populates="product", cascade="all, delete-orphan")
