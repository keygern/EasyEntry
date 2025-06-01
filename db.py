# db.py
import os
from sqlmodel import SQLModel, create_engine

# 1. Decide which database URL to use
DB_URL = os.getenv("DATABASE_URL")  # set in Render or .env

if not DB_URL:
    DB_URL = "sqlite:///easyentry.db"        # local default

# 2. If URL has no driver hint, force psycopg2 for safety
if DB_URL.startswith("postgresql://"):
    DB_URL = DB_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# 3. Build engine (SQLite needs the check_same_thread flag)
if DB_URL.startswith("sqlite"):
    engine = create_engine(
        DB_URL, echo=False,
        connect_args={"check_same_thread": False})
else:
    engine = create_engine(DB_URL, echo=False)

def create_db_and_tables():
    from models import ColumnMapping          # avoid circular import
    SQLModel.metadata.create_all(engine)
