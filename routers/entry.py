from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
import json

from db import engine
from models import ColumnMappingIn, ColumnMapping
from services import ocr
from services.parser import blocks_to_lines
from tasks import process_textract_job
from routers.auth import verify_supabase_jwt

router = APIRouter(prefix="/documents", tags=["documents"],
                   dependencies=[Depends(verify_supabase_jwt)])


@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_invoice(file: UploadFile = File(...), user_id: str = Depends(verify_supabase_jwt)):
    if file.content_type not in ("application/pdf", "image/jpeg", "image/png"):
        raise HTTPException(400, "Only PDF/JPG/PNG accepted")

    pdf_bytes = await file.read()
    s3_key = ocr.upload_to_s3(pdf_bytes)
    job_id = ocr.start_job(s3_key)
    process_textract_job.delay(job_id, "invoice", user_id)
    return {"job_id": job_id, "state": "processing"}


@router.get("/result/{job_id}")
def get_result(job_id: str):
    try:
        obj = ocr.s3.get_object(Bucket=ocr.BUCKET, Key=f"{ocr.RESULT_PREFIX}{job_id}.json")
    except ocr.s3.exceptions.NoSuchKey:
        raise HTTPException(404, "Still processing")
    blocks = json.loads(obj["Body"].read())
    return JSONResponse({"block_count": len(blocks), "blocks": blocks})


@router.get("/progress/{job_id}")
def get_progress(job_id: str):
    resp = ocr.tex.get_document_analysis(JobId=job_id)
    status = resp["JobStatus"]
    if status == "FAILED":
        raise HTTPException(500, "Textract job failed")
    if status == "SUCCEEDED":
        return {"status": "completed", "percent": 100}
    total = resp.get("TotalPages", 1)
    current = resp.get("PagesProcessed", 0)
    percent = int(current / total * 100)
    return {"status": "processing", "percent": percent}


def _fetch_blocks(job_id: str):
    try:
        obj = ocr.s3.get_object(Bucket=ocr.BUCKET, Key=f"{ocr.RESULT_PREFIX}{job_id}.json")
    except ocr.s3.exceptions.NoSuchKey:
        raise HTTPException(404, "Still processing")
    return json.loads(obj["Body"].read())


@router.get("/parsed/{seller_id}/{job_id}")
def get_parsed(seller_id: str, job_id: str):
    blocks = _fetch_blocks(job_id)
    with Session(engine) as db:
        lines = blocks_to_lines(blocks, seller_id, db)
    if lines:
        return {"line_count": len(lines), "lines": [l.dict() for l in lines], "needs_mapping": False}
    sample_rows = [b["Text"] for b in blocks if b["BlockType"] == "LINE"][:10]
    return {"needs_mapping": True, "sample_lines": sample_rows}


@router.post("/column-mapping/{seller_id}")
def save_mapping(seller_id: str, payload: ColumnMappingIn):
    with Session(engine) as db:
        rec = db.exec(select(ColumnMapping).where(ColumnMapping.seller_id == seller_id)).first()
        if rec:
            rec.mapping = payload.dict()
        else:
            rec = ColumnMapping(seller_id=seller_id, mapping=payload.dict())
        db.add(rec)
        db.commit()
    return {"status": "saved"}


