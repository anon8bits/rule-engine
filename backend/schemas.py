from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List

class NodeBase(BaseModel):
    type: str
    operator: Optional[str] = None
    field: Optional[str] = None
    value: Optional[Any] = None
    left: Optional['NodeBase'] = None
    right: Optional['NodeBase'] = None

    class Config:
        orm_mode = True

class RuleCombineRequest(BaseModel):
    rule_ids: List[int]
    save_rule: bool = False
    name: Optional[str] = None
    description: Optional[str] = None

class RuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    rule_string: str

class RuleCreate(RuleBase):
    pass

class Rule(RuleBase):
    id: int
    ast_json: Dict
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class RuleEvaluationCreate(BaseModel):
    input_data: Dict[str, Any]

class RuleEvaluation(BaseModel):
    id: int
    rule_id: int
    input_data: Dict[str, Any]
    result: bool
    evaluated_at: datetime

    class Config:
        orm_mode = True

NodeBase.model_rebuild()