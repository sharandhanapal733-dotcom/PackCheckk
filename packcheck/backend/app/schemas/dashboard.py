from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.schemas.inspection import InspectionSummaryResponse

class StatSummary(BaseModel):
    total_inspections: int
    compliant_count: int
    non_compliant_count: int
    manual_review_count: int
    total_violations: int
    average_compliance_score: float

class StatusDistribution(BaseModel):
    status: str
    label: str
    count: int
    percentage: float
    color: str

class ViolationCategoryStat(BaseModel):
    category: str
    count: int

class TrendDataPoint(BaseModel):
    date: str
    total: int
    compliant: int
    non_compliant: int
    manual_review: int

class CommonViolationItem(BaseModel):
    field_name: str
    violation_type: str
    count: int
    legal_reference: str

class DashboardResponse(BaseModel):
    stats: StatSummary
    status_distribution: List[StatusDistribution]
    violations_by_category: List[ViolationCategoryStat]
    trend_data: List[TrendDataPoint]
    common_violations: List[CommonViolationItem]
    recent_inspections: List[InspectionSummaryResponse]
