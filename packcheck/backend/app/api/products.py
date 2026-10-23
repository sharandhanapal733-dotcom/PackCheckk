from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.inspection import Inspection
from app.schemas.inspection import ProductResponse
from app.services.auth_service import get_current_user
from app.api.inspections import format_inspection_summary

router = APIRouter(prefix="/api/products", tags=["Product Repository"])

@router.get("", response_model=List[ProductResponse])
def list_products(
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Product)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(search_fmt)) |
            (Product.brand.ilike(search_fmt)) |
            (Product.identifier.ilike(search_fmt))
        )
    return query.order_by(desc(Product.created_at)).limit(limit).all()

@router.get("/{id}/history")
def get_product_inspection_history(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns previous inspections, historical compliance results, and violations for this product.
    Allows comparing changes across batches and time.
    """
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    inspections = db.query(Inspection).filter(Inspection.product_id == id).order_by(desc(Inspection.inspection_date)).all()

    history = []
    for insp in inspections:
        summary = format_inspection_summary(insp)
        summary["violations"] = [
            {
                "id": v.id,
                "field_name": v.field_name,
                "violation_type": v.violation_type,
                "severity": v.severity,
                "description": v.description,
            } for v in insp.violations
        ]
        summary["images"] = [
            {"id": img.id, "file_path": img.file_path, "original_filename": img.original_filename}
            for img in insp.images
        ]
        history.append(summary)

    return {
        "product": {
            "id": product.id,
            "name": product.name,
            "brand": product.brand,
            "category": product.category,
            "manufacturer": product.manufacturer,
            "identifier": product.identifier,
        },
        "total_inspections": len(history),
        "inspections": history
    }
