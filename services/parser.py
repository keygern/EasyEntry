# services/parser.py
import re
from typing import List
from models import InvoiceLine

_price_re = re.compile(r"\d[\d,]*\.\d{2}$")   # e.g. 1,234.56
_int_re   = re.compile(r"^\d+$")

def blocks_to_lines(blocks) -> List[InvoiceLine]:
    lines: list[InvoiceLine] = []

    for b in blocks:
        if b["BlockType"] != "LINE":
            continue

        text = " ".join(b["Text"].split())     # collapse multiple spaces
        tokens = text.split(" ")

        # need at least 3 tokens: desc ... qty price
        if len(tokens) < 3:
            continue

        price_token = tokens[-1]
        qty_token   = tokens[-2]

        if not _price_re.match(price_token):
            continue
        if not _int_re.match(qty_token):
            continue

        try:
            qty   = int(qty_token)
            price = float(price_token.replace(",", ""))
            desc  = " ".join(tokens[:-2])
            if desc:                             # ignore blank desc
                lines.append(
                    InvoiceLine(description=desc,
                                quantity=qty,
                                value=price))
        except ValueError:
            continue

    return lines
