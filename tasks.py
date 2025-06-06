import os
from celery import Celery
from services import ocr

CELERY_BROKER = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
celery_app = Celery('easyentry', broker=CELERY_BROKER)


@celery_app.task(name='process_textract_job')
def process_textract_job(job_id: str, doc_type: str, user_id: str) -> None:
    """Poll Textract and save blocks to S3."""
    ocr.poll_job(job_id)

