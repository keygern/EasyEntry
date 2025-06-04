import os
from celery import Celery
from typing import Dict, List
from services import ocr
from services import parser
from parsers import invoice as invoice_parser
from parsers import form3461, form7501
import json

CELERY_BROKER = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_BACKEND = os.getenv("CELERY_BACKEND_URL", CELERY_BROKER)

celery_app = Celery("easyentry", broker=CELERY_BROKER, backend=CELERY_BACKEND)

@celery_app.task
def process_textract_job(job_id: str, doc_type: str, user_id: str) -> str:
    # poll job until finished
    ocr.poll_job(job_id)
    blocks = ocr.fetch_blocks(job_id)

    result: Dict = {"status": "ok"}
    if doc_type == "invoice":
        from sqlmodel import Session
        from db import engine
        with Session(engine) as db:
            res = invoice_parser.parse_invoice(blocks, user_id, db)
            result.update({"needs_mapping": res.needs_mapping,
                           "data": [l.dict() for l in res.lines],
                           "sample_lines": res.sample_lines})
    elif doc_type == "3461":
        form = form3461.parse_form(blocks)
        result["data"] = form.dict()
    elif doc_type == "7501":
        form = form7501.parse_form(blocks)
        result["data"] = form.dict()
    else:
        result = {"status": "error", "detail": "unknown doc_type"}

    ocr.save_parsed(job_id, result)
    return job_id
