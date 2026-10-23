from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel
from app.models.rule import RuleType, RuleSeverity

class RuleBase(BaseModel):
    rule_id: str
    field: str
    rule_type: RuleType
    description: str
    severity: RuleSeverity
    legal_reference: str
    enabled: bool = True
    parameters: Optional[dict] = None

class RuleCreate(RuleBase):
    pass

class RuleUpdate(BaseModel):
    description: Optional[str] = None
    severity: Optional[RuleSeverity] = None
    legal_reference: Optional[str] = None
    enabled: Optional[bool] = None
    parameters: Optional[dict] = None

class RuleResponse(RuleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
