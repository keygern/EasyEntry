from sqlmodel import SQLModel, create_engine
from os import getenv

DATABASE_URL = getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=False)   # sync engine

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)