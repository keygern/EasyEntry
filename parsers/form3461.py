from typing import Dict, List
from pydantic import BaseModel

class Form3461(BaseModel):
    importer: str | None = None
    entry_number: str | None = None
    port: str | None = None


def extract_key_values(blocks: List[Dict]) -> Dict[str, str]:
    kv = {}
    keys = {b["Id"]: b for b in blocks if b["BlockType"] == "KEY_VALUE_SET" and "KEY" in b.get("EntityTypes", [])}
    vals = {b["Id"]: b for b in blocks if b["BlockType"] == "KEY_VALUE_SET" and "VALUE" in b.get("EntityTypes", [])}
    for key in keys.values():
        for rel in key.get("Relationships", []):
            if rel["Type"] == "VALUE":
                val_block = vals.get(rel["Ids"][0])
                if val_block:
                    k = key.get("Text", "").strip()
                    v = val_block.get("Text", "").strip()
                    if k:
                        kv[k] = v
    return kv

def parse_form(blocks: List[Dict]) -> Form3461:
    kv = extract_key_values(blocks)
    return Form3461(
        importer=kv.get("Importer"),
        entry_number=kv.get("Entry No."),
        port=kv.get("Port")
    )
