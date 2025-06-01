
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, status
from services import ocr
from fastapi.responses import JSONResponse
import json
from services.parser import blocks_to_lines
from sqlmodel import Session, select
from db import engine              # your SQLModel engine
from models import ColumnMappingIn, ColumnMapping

RESULT_PREFIX = "results/" 

router = APIRouter(prefix="/entries", tags=["entries"])

@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_invoice(
    bg: BackgroundTasks,
    file: UploadFile = File(...),
):
    if file.content_type not in ("application/pdf", "image/jpeg", "image/png"):
        raise HTTPException(400, "Only PDF/JPG/PNG accepted")

    pdf_bytes = await file.read()
    s3_key = ocr.upload_to_s3(pdf_bytes)
    job_id  = ocr.start_job(s3_key)
    bg.add_task(ocr.poll_job, job_id)       # non-blocking

    return {"job_id": job_id, "state": "processing"}

@router.get("/result/{job_id}")
def get_result(job_id: str):
    try:
        obj = ocr.s3.get_object(
            Bucket=ocr.BUCKET,
            Key=f"{ocr.RESULT_PREFIX}{job_id}.json")
    except ocr.s3.exceptions.NoSuchKey:
        raise HTTPException(404, "Still processing")
    blocks = json.loads(obj["Body"].read())
    return JSONResponse({"block_count": len(blocks), "blocks": blocks})

async def upload_invoice(
    bg: BackgroundTasks,
    file: UploadFile = File(...)
):
    if file.content_type not in ("application/pdf", "image/jpeg", "image/png"):
        raise HTTPException(400, "Only PDF/JPG/PNG accepted")

    pdf = await file.read()
    s3_key = ocr.upload_to_s3(pdf)
    job_id = ocr.start_job(s3_key)

    # background poll (non-blocking request)
    bg.add_task(ocr.poll_job, job_id)

    return {"job_id": job_id, "state": "processing"}

@router.get("/entries/progress/{job_id}")
def get_progress(job_id: str):
    """Return real Textract progress as a percent (0-100)."""
    resp = ocr.tex.get_document_analysis(JobId=job_id)
    status = resp["JobStatus"]

    if status == "FAILED":
        raise HTTPException(500, "Textract job failed")
    if status == "SUCCEEDED":
        return {"status": "completed", "percent": 100}

    # IN_PROGRESS
    total   = resp.get("TotalPages", 1)
    current = resp.get("PagesProcessed", 0)
    percent = int(current / total * 100)
    return {"status": "processing", "percent": percent}

def _fetch_blocks(job_id: str):
    try:
        obj = ocr.s3.get_object(
            Bucket=ocr.BUCKET,
            Key=f"{ocr.RESULT_PREFIX}{job_id}.json")
    except ocr.s3.exceptions.NoSuchKey:
        raise HTTPException(404, "Still processing")
    return json.loads(obj["Body"].read())

@router.get("/entries/parsed/{seller_id}/{job_id}")
def get_parsed(seller_id: str, job_id: str):
    blocks = _fetch_blocks(job_id)
    with Session(engine) as db:
        lines = blocks_to_lines(blocks, seller_id, db)

    if lines:
        return {"line_count": len(lines),
                "lines": [l.dict() for l in lines],
                "needs_mapping": False}

    sample_rows = [
        b["Text"] for b in blocks if b["BlockType"] == "LINE"
    ][:10]

    return {"needs_mapping": True, "sample_lines": sample_rows}

@router.post("/column-mapping/{seller_id}")
def save_mapping(seller_id: str, payload: ColumnMappingIn):
    with Session(engine) as db:
        rec = db.exec(
            select(ColumnMapping)
            .where(ColumnMapping.seller_id == seller_id)
        ).first()

        if rec:
            rec.mapping = payload.dict()
        else:
            rec = ColumnMapping(
                seller_id=seller_id,
                mapping=payload.dict())
        db.add(rec)
        db.commit()
    return {"status": "saved"}