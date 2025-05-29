
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, status
from services import ocr
from fastapi.responses import JSONResponse
import json

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


