from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from . import crud, schemas, parser, evaluator, models
from .database import get_db, create_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

app = FastAPI(
    title="Rule Engine API",
    lifespan=lifespan
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize parser and evaluator
rule_parser = parser.RuleParser()
rule_evaluator = evaluator.RuleEvaluator()

@app.post("/api/rules/", response_model=schemas.Rule)
async def create_rule(rule: schemas.RuleCreate, db: Session = Depends(get_db)):
    try:
        # Parse rule string to AST
        ast = rule_parser.create_rule(rule.rule_string)
        # Create rule in database
        db_rule = crud.RuleRepository.create_rule(db, rule, ast.dict())
        return db_rule
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/rules/", response_model=List[schemas.Rule])
async def get_rules(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    rules = crud.RuleRepository.get_rules(db, skip=skip, limit=limit)
    return rules

@app.get("/api/rules/{rule_id}", response_model=schemas.Rule)
async def get_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = crud.RuleRepository.get_rule(db, rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

@app.put("/api/rules/{rule_id}", response_model=schemas.Rule)
async def update_rule(
    rule_id: int, 
    rule: schemas.RuleCreate, 
    db: Session = Depends(get_db)
):
    try:
        # Parse updated rule string to AST
        ast = rule_parser.create_rule(rule.rule_string)
        # Update rule in database
        db_rule = crud.RuleRepository.update_rule(db, rule_id, rule, ast.dict())
        if db_rule is None:
            raise HTTPException(status_code=404, detail="Rule not found")
        return db_rule
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/rules/{rule_id}")
async def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    success = crud.RuleRepository.delete_rule(db, rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"message": "Rule deleted successfully"}

@app.post("/api/rules/{rule_id}/evaluate")
async def evaluate_rule(
    rule_id: int, 
    data: Dict[str, Any], 
    db: Session = Depends(get_db)
):
    rule = crud.RuleRepository.get_rule(db, rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
        
    try:
        # Convert stored AST back to NodeBase
        ast = schemas.NodeBase.model_validate(rule.ast_json)
        # Evaluate rule
        result = rule_evaluator.evaluate_rule(ast, data)
        
        # Store evaluation result
        evaluation = crud.RuleRepository.create_evaluation(
            db=db,
            rule_id=rule_id,
            input_data=data,
            result=result
        )
        
        return {
            "rule_id": rule_id,
            "result": result,
            "evaluation_id": evaluation.id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/rules/{rule_id}/evaluations", response_model=List[schemas.RuleEvaluation])
async def get_rule_evaluations(
    rule_id: int, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    rule = crud.RuleRepository.get_rule(db, rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
        
    evaluations = crud.RuleRepository.get_rule_evaluations(
        db, rule_id, skip=skip, limit=limit
    )
    return evaluations

@app.post("/api/rules/combine")
async def combine_rules(
    request: schemas.RuleCombineRequest,
    db: Session = Depends(get_db)
):
    # Get all rules
    rules = []
    for rule_id in request.rule_ids:
        rule = crud.RuleRepository.get_rule(db, rule_id)
        if rule is None:
            raise HTTPException(
                status_code=404, 
                detail=f"Rule with id {rule_id} not found"
            )
        rules.append(schemas.NodeBase.model_validate(rule.ast_json))
    
    try:
        # Combine rules
        combined_ast = rule_evaluator.combine_rules(rules)
        
        if request.save_rule:
            # For saving, we'll use a simplified rule string representation
            rule_strings = [
                crud.RuleRepository.get_rule(db, rule_id).rule_string 
                for rule_id in request.rule_ids
            ]
            combined_rule_string = f"({' OR '.join(rule_strings)})"
            
            # Save as new rule
            new_rule = schemas.RuleCreate(
                name=request.name or f"Combined Rule ({','.join(map(str, request.rule_ids))})",
                description=request.description or f"Combination of rules: {request.rule_ids}",
                rule_string=combined_rule_string
            )
            
            db_rule = crud.RuleRepository.create_rule(
                db=db,
                rule=new_rule,
                ast_json=combined_ast.model_dump()
            )
            
            return {
                "rule_id": db_rule.id,
                "name": db_rule.name,
                "rule_string": combined_rule_string,
                "ast": combined_ast.model_dump()
            }
        
        # Return just the combined AST if not saving
        return {
            "ast": combined_ast.model_dump()
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))