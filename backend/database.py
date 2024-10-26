from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLITE_URL = "sqlite:///rule_engine.db"
engine = create_engine(SQLITE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def create_tables():
    # Create tables using raw SQL
    with engine.connect() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR NOT NULL,
            description VARCHAR,
            rule_string VARCHAR NOT NULL,
            ast_json JSON NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """))
        
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS rule_evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_id INTEGER NOT NULL,
            input_data JSON NOT NULL,
            result BOOLEAN NOT NULL,
            evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (rule_id) REFERENCES rules(id)
        )
        """))
        
        # Create an index on rule_id for better query performance
        conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_rule_evaluations_rule_id 
        ON rule_evaluations(rule_id)
        """))
        
        conn.commit()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()