from typing import List, Dict, Tuple
from sqlmodel import Session, select
from models import InvoiceLine, ColumnMapping
from services import parser

class InvoiceParseResult:
    def __init__(self, lines: List[InvoiceLine] | None = None, needs_mapping: bool = False, sample_lines: List[str] | None = None):
        self.lines = lines or []
        self.needs_mapping = needs_mapping
        self.sample_lines = sample_lines or []

def parse_invoice(blocks: List[Dict], seller_id: str, db: Session) -> InvoiceParseResult:
    rows = parser.textract_tables(blocks)
    mapping_rec = db.exec(
        select(ColumnMapping).where(ColumnMapping.seller_id == seller_id)
    ).first()
    mapping = mapping_rec.mapping if mapping_rec else parser.detect_columns(rows)

    if not mapping:
        sample = [b["Text"] for b in blocks if b.get("BlockType") == "LINE"][:10]
        return InvoiceParseResult(needs_mapping=True, sample_lines=sample)

    qty_i = mapping["qty_col"]
    val_i = mapping["val_col"]
    lines: List[InvoiceLine] = []
    for row in rows.values():
        try:
            qty_cell = next(c for c in row if c["ColumnIndex"] == qty_i)
            val_cell = next(c for c in row if c["ColumnIndex"] == val_i)
            qty = int(parser._clean(qty_cell["Text"]))
            value = float(parser._clean(val_cell["Text"]).replace(",", ""))
            desc = " ".join(
                c["Text"] for c in row if c["ColumnIndex"] not in (qty_i, val_i)
            ).strip()
            if desc:
                lines.append(InvoiceLine(description=desc, quantity=qty, value=value))
        except (StopIteration, ValueError):
            continue
    return InvoiceParseResult(lines=lines)

