from collections import Counter
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.inspection import (
    Inspection,
    InspectionStatus,
    Violation
)
from app.schemas.dashboard import (
    DashboardResponse,
    StatSummary,
    StatusDistribution,
    ViolationCategoryStat,
    TrendDataPoint,
    CommonViolationItem
)
from app.services.auth_service import get_current_user
from app.api.inspections import format_inspection_summary

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("", response_model=DashboardResponse)
def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Total counts
    total_inspections = db.query(Inspection).count()
    compliant_count = db.query(Inspection).filter(Inspection.overall_status == InspectionStatus.COMPLIANT).count()
    non_compliant_count = db.query(Inspection).filter(Inspection.overall_status == InspectionStatus.POTENTIAL_NON_COMPLIANCE).count()
    manual_review_count = db.query(Inspection).filter(Inspection.overall_status == InspectionStatus.MANUAL_REVIEW_REQUIRED).count()
    total_violations = db.query(Violation).count()

    # Average score
    avg_score = db.query(func.avg(Inspection.compliance_score)).scalar() or 0.0

    stats = StatSummary(
        total_inspections=total_inspections,
        compliant_count=compliant_count,
        non_compliant_count=non_compliant_count,
        manual_review_count=manual_review_count,
        total_violations=total_violations,
        average_compliance_score=round(float(avg_score), 1)
    )

    # 2. Status distribution
    tot_safe = total_inspections if total_inspections > 0 else 1
    status_distribution = [
        StatusDistribution(
            status="COMPLIANT",
            label="Compliant",
            count=compliant_count,
            percentage=round((compliant_count / tot_safe) * 100, 1),
            color="#10b981"
        ),
        StatusDistribution(
            status="POTENTIAL_NON_COMPLIANCE",
            label="Potential Non-Compliance",
            count=non_compliant_count,
            percentage=round((non_compliant_count / tot_safe) * 100, 1),
            color="#ef4444"
        ),
        StatusDistribution(
            status="MANUAL_REVIEW_REQUIRED",
            label="Manual Review Required",
            count=manual_review_count,
            percentage=round((manual_review_count / tot_safe) * 100, 1),
            color="#f59e0b"
        ),
    ]

    # 3. Violations by category
    viol_cats = db.query(
        Violation.violation_type,
        func.count(Violation.id)
    ).group_by(Violation.violation_type).all()

    violations_by_category = [
        ViolationCategoryStat(category=cat.replace('_', ' ').title(), count=cnt)
        for cat, cnt in viol_cats
    ]

    # 4. Inspections over time (Last 7 days or all records grouped by day)
    trend_dict = {}
    # Initialize past 7 days
    today = datetime.utcnow().date()
    for d in range(6, -1, -1):
        dt_str = (today - timedelta(days=d)).strftime("%d %b")
        trend_dict[dt_str] = {"total": 0, "compliant": 0, "non_compliant": 0, "manual_review": 0}

    all_inspections = db.query(Inspection.inspection_date, Inspection.overall_status).all()
    for insp_date, insp_status in all_inspections:
        key = insp_date.strftime("%d %b")
        if key in trend_dict:
            trend_dict[key]["total"] += 1
            if insp_status == InspectionStatus.COMPLIANT:
                trend_dict[key]["compliant"] += 1
            elif insp_status == InspectionStatus.POTENTIAL_NON_COMPLIANCE:
                trend_dict[key]["non_compliant"] += 1
            elif insp_status == InspectionStatus.MANUAL_REVIEW_REQUIRED:
                trend_dict[key]["manual_review"] += 1

    trend_data = [
        TrendDataPoint(
            date=k,
            total=v["total"],
            compliant=v["compliant"],
            non_compliant=v["non_compliant"],
            manual_review=v["manual_review"]
        ) for k, v in trend_dict.items()
    ]

    # 5. Most common violations
    common_viols_query = db.query(
        Violation.field_name,
        Violation.violation_type,
        Violation.legal_reference,
        func.count(Violation.id).label("count")
    ).group_by(Violation.field_name, Violation.violation_type, Violation.legal_reference).order_by(desc("count")).limit(5).all()

    common_violations = [
        CommonViolationItem(
            field_name=item[0].replace('_', ' ').title(),
            violation_type=item[1].replace('_', ' ').title(),
            count=item[3],
            legal_reference=item[2]
        ) for item in common_viols_query
    ]

    # 6. Recent inspections
    recent_inspections_db = db.query(Inspection).order_by(desc(Inspection.inspection_date)).limit(8).all()
    recent_inspections = [format_inspection_summary(insp) for insp in recent_inspections_db]

    return DashboardResponse(
        stats=stats,
        status_distribution=status_distribution,
        violations_by_category=violations_by_category,
        trend_data=trend_data,
        common_violations=common_violations,
        recent_inspections=recent_inspections
    )
