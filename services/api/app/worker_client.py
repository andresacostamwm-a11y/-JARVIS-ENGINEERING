"""Enqueue Celery tasks when broker is available."""
from app.core.config import get_settings


def enqueue_document_ingest(document_id: str) -> None:
    settings = get_settings()
    from celery import Celery

    app = Celery("jarvis", broker=settings.celery_broker_url)
    app.send_task("worker.tasks.ingest_document", args=[document_id])
