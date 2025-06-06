import boto3, os
from typing import List, Dict
from fastapi import HTTPException

textract = boto3.client(
    "textract",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION", "us-east-1"),
)

MAX_TEST_PAGES = 200
pages_used = 0

def extract_blocks(pdf_bytes: bytes) -> List[Dict]:
    global pages_used
    if pages_used >= MAX_TEST_PAGES:
        raise HTTPException(429, "Daily Textract test limit reached")

    resp = textract.analyze_document(
        Document={"Bytes": pdf_bytes},
        FeatureTypes=["TABLES", "FORMS"],
    )

    pages_used += resp["DocumentMetadata"]["Pages"]
    return resp["Blocks"]

