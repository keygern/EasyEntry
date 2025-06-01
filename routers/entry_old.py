from fastapi import APIRouter, UploadFile, File, HTTPException
from services.ocr_old import extract_blocks

router = APIRouter(prefix="/entries", tags=["entries"])

@router.post("/upload")
async def upload_invoice(file: UploadFile = File(...)):
    if file.content_type not in ("application/pdf", "image/jpeg", "image/png"):
        raise HTTPException(400, "Only PDF or image invoices accepted")

    data = await file.read()          # bytes
    blocks = extract_blocks(data)     # raw Textract blocks

    """# TODO: smarter parse in next step"""
    return {"block_count": len(blocks), "raw": blocks[:25]}  # truncate for demo
