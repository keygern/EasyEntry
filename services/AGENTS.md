# OCR & Parsing Agent Guide

## Flow
1. `services/ocr.py`
   - Upload file to S3 → `uploads/{uuid}.{ext}`
   - Start **async** Textract job (TABLES & FORMS)
   - Return `job_id`

2. Celery task `process_textract_job(job_id, doc_type, user_id)`
   1. Poll Textract → when SUCCEEDED save raw blocks JSON to `results/{job_id}.json`.
   2. Call parser:
      * `parsers/invoice.py`
      * `parsers/form3461.py`
      * `parsers/form7501.py`
   3. Store parsed JSON to `results/{job_id}_parsed.json`.
   4. If doc_type in {3461, 7501} generate PDF (`pdf/{job_id}.pdf`) via ReportLab.

## Parsing modules
* **Invoice**
  - Use `ColumnMapping` if exists; else auto-detect numeric qty/value cols (≥80 % numeric).
  - On low confidence, return `needs_mapping=true` + sample lines.
* **Forms**
  - Use `extract_key_values(blocks)` helper (KEY_VALUE_SET pairing).
  - Return `Form3461` / `Form7501` Pydantic models.

### Errors
Raise `ParserError(detail="…")`; Celery stores `{ "status":"error", "detail": … }`.
