from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse
from .auth import verify_supabase_jwt
from services import ocr
from services.tasks import process_textract_job
from models import ColumnMappingIn, ColumnMapping, UserPlan
from db import engine
from sqlmodel import Session, select
import json

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_TYPES = {"invoice", "3461", "7501"}

@router.post("/upload", status_code=202)
async def upload_document(bg: BackgroundTasks, doc_type: str, file: UploadFile = File(...), user_id: str = Depends(verify_supabase_jwt)):
    if doc_type not in ALLOWED_TYPES:
        raise HTTPException(400, "unknown doc_type")
    if file.content_type not in ("application/pdf", "image/jpeg", "image/png"):
        raise HTTPException(400, "Only PDF/JPG/PNG accepted")

    with Session(engine) as db:
        plan = db.exec(select(UserPlan).where(UserPlan.user_id == user_id)).first()
        if not plan:
            plan = UserPlan(user_id=user_id)
            db.add(plan)
            db.commit()
        if plan.plan != "pro" and plan.quota_remaining <= 0:
            raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, "Quota exceeded")

        data = await file.read()
        s3_key = ocr.upload_to_s3(data)
        job_id = ocr.start_job(s3_key)
        process_textract_job.delay(job_id, doc_type, user_id)

        if plan.plan != "pro":
            plan.quota_remaining -= 1
            db.add(plan)
            db.commit()

    return {"job_id": job_id}

@router.get("/parse/{doc_type}/{job_id}")
def get_parse(doc_type: str, job_id: str, user_id: str = Depends(verify_supabase_jwt)):
    try:
        resp = ocr.s3.get_object(Bucket=ocr.BUCKET, Key=f"{ocr.RESULT_PREFIX}{job_id}_parsed.json")
    except ocr.s3.exceptions.NoSuchKey:
        raise HTTPException(404, "processing")
    data = json.loads(resp["Body"].read())
    return data

@router.post("/column-mapping", status_code=204)
def save_mapping(payload: ColumnMappingIn, user_id: str = Depends(verify_supabase_jwt)):
    with Session(engine) as db:
        rec = db.exec(select(ColumnMapping).where(ColumnMapping.seller_id == user_id)).first()
        if rec:
            rec.mapping = payload.dict()
        else:
            rec = ColumnMapping(seller_id=user_id, mapping=payload.dict())
        db.add(rec)
        db.commit()
    return JSONResponse(status_code=204)

@router.get("/pdf/{doc_type}/{job_id}")
def get_pdf(doc_type: str, job_id: str, user_id: str = Depends(verify_supabase_jwt)):
    key = f"{ocr.RESULT_PREFIX}{job_id}_parsed.json"  # pdf path uses same prefix
    pdf_key = f"pdf/{job_id}.pdf"
    try:
        obj = ocr.s3.get_object(Bucket=ocr.BUCKET, Key=pdf_key)
    except ocr.s3.exceptions.NoSuchKey:
        raise HTTPException(404, "pdf not ready")
    return StreamingResponse(obj["Body"], media_type="application/pdf")

