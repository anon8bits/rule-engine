from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Rule(Base):
    __tablename__ = "rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    rule_string = Column(String, nullable=False)
    ast_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    evaluations = relationship("RuleEvaluation", back_populates="rule")

class RuleEvaluation(Base):
    __tablename__ = "rule_evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("rules.id"))
    input_data = Column(JSON, nullable=False)
    result = Column(Boolean, nullable=False)
    evaluated_at = Column(DateTime, default=datetime.now)
    
    rule = relationship("Rule", back_populates="evaluations")