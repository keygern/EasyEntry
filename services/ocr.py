import os, uuid, boto3, json, time, logging
from typing import List, Dict

AWS_REGION   = os.getenv("AWS_REGION", "us-east-1")
BUCKET       = os.getenv("AWS_S3_BUCKET")          # must exist
RESULT_PREFIX = "results/"                         # single source of truth
assert BUCKET, "AWS_S3_BUCKET missing"

s3  = boto3.client("s3", region_name=AWS_REGION)
tex = boto3.client("textract", region_name=AWS_REGION)

log = logging.getLogger("ocr")

# ── helpers ────────────────────────────────────────────────────────────────
def upload_to_s3(data: bytes) -> str:
    key = f"tmp/{uuid.uuid4()}.pdf"
    s3.put_object(Bucket=BUCKET, Key=key, Body=data)
    return key

def start_job(s3_key: str) -> str:
    resp = tex.start_document_analysis(
        DocumentLocation={"S3Object": {"Bucket": BUCKET, "Name": s3_key}},
        FeatureTypes=["TABLES", "FORMS"],
    )
    return resp["JobId"]

def _save_result(job_id: str, blocks: List[Dict]) -> None:
    """Write finished blocks into results/ folder as JSON bytes."""
    s3.put_object(
        Bucket=BUCKET,
        Key=f"{RESULT_PREFIX}{job_id}.json",
        Body=json.dumps(blocks).encode("utf-8"),
    )

def fetch_blocks(job_id: str) -> List[Dict]:
    resp = s3.get_object(Bucket=BUCKET, Key=f"{RESULT_PREFIX}{job_id}.json")
    return json.loads(resp["Body"].read())

def save_parsed(job_id: str, data: Dict) -> None:
    s3.put_object(
        Bucket=BUCKET,
        Key=f"{RESULT_PREFIX}{job_id}_parsed.json",
        Body=json.dumps(data).encode("utf-8"),
    )

# ── main polling function (runs in background thread) ─────────────────────
def poll_job(job_id: str, *, max_try=60, wait=5) -> None:
    """
    Poll Textract until SUCCEEDED or FAILED, then save blocks to S3.
    Runs in a FastAPI BackgroundTask, so blocking sleep is fine.
    """
    for _ in range(max_try):
        resp = tex.get_document_analysis(JobId=job_id)
        job_status = resp["JobStatus"]

        if job_status == "SUCCEEDED":
            blocks = resp["Blocks"]
            log.info("Textract finished, %s blocks", len(blocks))
            _save_result(job_id, blocks)
            return                                  # done ✔
        if job_status == "FAILED":
            log.error("Textract job %s failed", job_id)
            return

        time.sleep(wait)                            # still IN_PROGRESS
    log.error("Textract job %s timed-out", job_id)
