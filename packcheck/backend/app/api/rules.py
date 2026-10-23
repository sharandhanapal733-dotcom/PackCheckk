from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.rule import ComplianceRule
from app.schemas.rule import RuleCreate, RuleUpdate, RuleResponse
from app.services.auth_service import get_current_user, require_admin

router = APIRouter(prefix="/api/rules", tags=["Compliance Rules"])

@router.get("", response_model=List[RuleResponse])
def get_all_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rules = db.query(ComplianceRule).order_by(ComplianceRule.id).all()
    return rules

@router.post("", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
def create_rule(
    rule_in: RuleCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    existing = db.query(ComplianceRule).filter(ComplianceRule.rule_id == rule_in.rule_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rule with ID '{rule_in.rule_id}' already exists."
        )

    rule = ComplianceRule(
        rule_id=rule_in.rule_id,
        field=rule_in.field,
        rule_type=rule_in.rule_type,
        description=rule_in.description,
        severity=rule_in.severity,
        legal_reference=rule_in.legal_reference,
        enabled=rule_in.enabled,
        parameters=rule_in.parameters,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule

@router.put("/{id}", response_model=RuleResponse)
def update_rule(
    id: int,
    rule_update: RuleUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    rule = db.query(ComplianceRule).filter(ComplianceRule.id == id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    if rule_update.description is not None:
        rule.description = rule_update.description
    if rule_update.severity is not None:
        rule.severity = rule_update.severity
    if rule_update.legal_reference is not None:
        rule.legal_reference = rule_update.legal_reference
    if rule_update.enabled is not None:
        rule.enabled = rule_update.enabled
    if rule_update.parameters is not None:
        rule.parameters = rule_update.parameters

    db.commit()
    db.refresh(rule)
    return rule

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(
    id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    rule = db.query(ComplianceRule).filter(ComplianceRule.id == id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
