from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime
from typing import List, Optional

class RuleRepository:
    @staticmethod
    def create_rule(db: Session, rule: schemas.RuleCreate, ast_json: dict):
        db_rule = models.Rule(
            name=rule.name,
            description=rule.description,
            rule_string=rule.rule_string,
            ast_json=ast_json
        )
        db.add(db_rule)
        db.commit()
        db.refresh(db_rule)
        return db_rule
    
    @staticmethod
    def get_rule(db: Session, rule_id: int) -> Optional[models.Rule]:
        return db.query(models.Rule).filter(models.Rule.id == rule_id).first()
    
    @staticmethod
    def get_rules(db: Session, skip: int = 0, limit: int = 100) -> List[models.Rule]:
        return db.query(models.Rule).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_rule(db: Session, rule_id: int, rule: schemas.RuleCreate, ast_json: dict) -> Optional[models.Rule]:
        db_rule = db.query(models.Rule).filter(models.Rule.id == rule_id).first()
        if db_rule:
            db_rule.name = rule.name
            db_rule.description = rule.description
            db_rule.rule_string = rule.rule_string
            db_rule.ast_json = ast_json
            db_rule.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_rule)
        return db_rule
    
    @staticmethod
    def delete_rule(db: Session, rule_id: int) -> bool:
        db_rule = db.query(models.Rule).filter(models.Rule.id == rule_id).first()
        if db_rule:
            db.delete(db_rule)
            db.commit()
            return True
        return False
    
    @staticmethod
    def create_evaluation(
        db: Session, 
        rule_id: int, 
        input_data: dict, 
        result: bool
    ) -> models.RuleEvaluation:
        evaluation = models.RuleEvaluation(
            rule_id=rule_id,
            input_data=input_data,
            result=result
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        return evaluation
    
    @staticmethod
    def get_rule_evaluations(
        db: Session, 
        rule_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[models.RuleEvaluation]:
        return db.query(models.RuleEvaluation)\
            .filter(models.RuleEvaluation.rule_id == rule_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
