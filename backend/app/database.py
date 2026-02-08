from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path

# 1. Use absolute path to database file in backend directory
# This ensures all scripts use the same database
BASE_DIR = Path(__file__).parent
DATABASE_PATH = BASE_DIR / "sql_app.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# 2. THE ENGINE
# CRITICAL: 'check_same_thread': False is required for SQLite only!
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 3. Helper to open/close the connection per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()