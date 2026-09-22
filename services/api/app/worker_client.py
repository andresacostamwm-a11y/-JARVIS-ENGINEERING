from celery import Celery
from app.core.config import get_settings
def enqueue_document_ingest(document_id:str):
 s=get_settings();Celery('jarvis',broker=s.celery_broker_url).send_task('worker.tasks.ingest_document',args=[document_id])
