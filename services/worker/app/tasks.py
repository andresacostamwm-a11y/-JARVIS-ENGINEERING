"""Celery tasks: document ingest / embeddings (MVP bag-of-words chunks)."""
from __future__ import annotations
import os
import sys

# Allow importing API package
sys.path.insert(0, "/api")

from app.celery_app import celery


@celery.task(name="worker.tasks.ingest_document")
def ingest_document(document_id: str) -> dict:
    from uuid import UUID
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models import Document, DocumentChunk  # type: ignore  # from /api
    from app.services.rag.search import chunk_text  # type: ignore
    from app.services.storage import get_object  # type: ignore

    db_url = os.getenv("DATABASE_URL", "postgresql+psycopg://jarvis:jarvis_dev_password@postgres:5432/jarvis")
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        doc = db.query(Document).filter(Document.id == UUID(document_id)).first()
        if not doc:
            return {"ok": False, "error": "not found"}
        doc.status = "processing"
        db.commit()
        try:
            data = get_object(doc.storage_key)
            text = data.decode("utf-8", errors="ignore")
        except Exception:
            text = f"[Could not decode {doc.filename}. PDF/DOCX extraction COMING SOON.]"
        if not text.strip():
            text = f"[Empty content for {doc.filename}]"
        db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).delete()
        for i, chunk in enumerate(chunk_text(text)):
            # embedding: null in MVP; store token presence as cheap "embedding" stub
            tokens = sorted({t.lower() for t in chunk.split() if len(t) > 2})[:64]
            db.add(
                DocumentChunk(
                    document_id=doc.id,
                    chunk_index=i,
                    content=chunk,
                    embedding=None,
                    meta={"token_sample": tokens, "engine": "celery-ingest-v1"},
                )
            )
        doc.status = "ready"
        db.commit()
        return {"ok": True, "document_id": document_id, "chunks": i + 1 if text else 0}
    except Exception as e:
        db.rollback()
        try:
            doc = db.query(Document).filter(Document.id == UUID(document_id)).first()
            if doc:
                doc.status = "failed"
                db.commit()
        except Exception:
            pass
        return {"ok": False, "error": str(e)}
    finally:
        db.close()
