import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum, JSON
from app.database import Base

class RuleType(str, enum.Enum):
    REQUIRED_FIELD = "REQUIRED_FIELD"
    PATTERN_VALIDATION = "PATTERN_VALIDATION"
    NUMERIC_VALIDATION = "NUMERIC_VALIDATION"
    DATE_VALIDATION = "DATE_VALIDATION"
    TEXT_READABILITY = "TEXT_READABILITY"
    FONT_SIZE_REVIEW = "FONT_SIZE_REVIEW"
    PLACEMENT_REVIEW = "PLACEMENT_REVIEW"

class RuleSeverity(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class ComplianceRule(Base):
    __tablename__ = "compliance_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(String(50), unique=True, index=True, nullable=False) # e.g. LMPC-R6-1A
    field = Column(String(100), index=True, nullable=False) # e.g. manufacturer, mrp, net_quantity
    rule_type = Column(Enum(RuleType), default=RuleType.REQUIRED_FIELD, nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(Enum(RuleSeverity), default=RuleSeverity.HIGH, nullable=False)
    legal_reference = Column(String(255), nullable=False) # e.g. "Rule 6(1)(a) of Legal Metrology (Packaged Commodities) Rules, 2011"
    enabled = Column(Boolean, default=True, nullable=False)
    parameters = Column(JSON, nullable=True) # Custom parameters e.g. min_confidence, valid_units
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
