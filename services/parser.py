# services/parser.py
import re
from typing import List, Dict
from models import InvoiceLine, ColumnMapping
from sqlmodel import Session, select

_QTY = re.compile(r"^\d{1,6}$")                     # 1 … 999999
_VAL = re.compile(r"^\$?\d[\d,]*\.\d{2}$")          # 1,234.56  or 1234.56

def textract_tables(blocks) -> Dict[int, List[Dict]]:
    cells = {b["Id"]: b for b in blocks if b["BlockType"] == "CELL"}
    rows: Dict[int, List[Dict]] = {}
    for cell in cells.values():
        rows.setdefault(cell["RowIndex"], []).append(cell)
    for r in rows.values():
        r.sort(key=lambda c: c["ColumnIndex"])
    return rows                       # {row_idx: [cell, cell, …]}

def detect_columns(table_rows) -> dict:
    """Return dict with keys qty, val (indices) or empty if confidence low."""
    col_stats = {}
    for row in table_rows.values():
        for cell in row:
            col = cell["ColumnIndex"]
            text = " ".join(cell["Text"].split())
            stat = col_stats.setdefault(col, {"qty": 0, "val": 0, "total": 0})
            stat["total"] += 1
            if _QTY.match(text):
                stat["qty"] += 1
            if _VAL.match(text):
                stat["val"] += 1

    def best(kind):
        cand = [
            (col, s[kind] / s["total"])
            for col, s in col_stats.items() if s[kind] > 0
        ]
        cand.sort(key=lambda t: t[1], reverse=True)
        return cand[0] if cand else (None, 0)

    qty_col, qty_conf = best("qty")
    val_col, val_conf = best("val")

    if qty_conf >= 0.8 and val_conf >= 0.8:
        return {"qty_col": qty_col, "val_col": val_col}
    return {}      # need user mapping

def blocks_to_lines(blocks, seller_id: str, db_session: Session) -> List[InvoiceLine]:
    rows = textract_tables(blocks)

    # 1. look for stored mapping
    mapping_rec = db_session.exec(
        select(ColumnMapping).where(ColumnMapping.seller_id == seller_id)
    ).first()

    if mapping_rec:
        mapping = mapping_rec.mapping
    else:
        mapping = detect_columns(rows)

    if not mapping:
        return []   # caller will interpret as "needs mapping"

    qty_i = mapping["qty_col"]
    val_i = mapping["val_col"]

    parsed = []
    for row in rows.values():
        try:
            qty_cell = next(c for c in row if c["ColumnIndex"] == qty_i)
            val_cell = next(c for c in row if c["ColumnIndex"] == val_i)
            qty   = int(_clean(qty_cell["Text"]))
            value = float(_clean(val_cell["Text"]).replace(",", ""))
            desc  = " ".join(
                c["Text"] for c in row
                if c["ColumnIndex"] not in (qty_i, val_i)
            ).strip()
            if desc:
                parsed.append(InvoiceLine(description=desc,
                                          quantity=qty,
                                          value=value))
        except (StopIteration, ValueError):
            continue
    return parsed

def _clean(t: str) -> str:
    return t.replace("$", "").replace(" ", "").strip()


