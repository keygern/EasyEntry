from typing import Optional
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Column, JSON

# ── API payloads ──────────────────────────────────────────────────────────
class InvoiceLine(BaseModel):
    description: str
    quantity: int
    value: float


class ColumnMappingIn(BaseModel):
    qty_col: int        # 1-based index
    val_col: int


# ── DB table (per seller) ────────────────────────────────────────────────
class ColumnMapping(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    seller_id: str = Field(index=True, unique=True)
    mapping: dict = Field(sa_column=Column(JSON))
