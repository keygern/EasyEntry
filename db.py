import os
from sqlmodel import SQLModel, create_engine

DB_URL = os.getenv("DATABASE_URL", "sqlite:///easyentry.db")

if DB_URL.startswith("sqlite"):
    engine = create_engine(DB_URL, echo=False, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DB_URL, echo=False)   # Postgres needs no connect_args
