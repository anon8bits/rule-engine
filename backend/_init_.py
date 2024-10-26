from .database import Base, engine
from .models import Rule, RuleEvaluation

# Create tables
Base.metadata.create_all(bind=engine)