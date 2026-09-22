from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Document, User
from app.schemas.common import DocumentOut
from app.api.deps import get_current_user, require_min_role
from app.models.entities import Role
from app.services.storage import put_object, get_object, ensure_bucket
from app.services.audit import write_audit

router = APIRouter()


@router.get("", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(Document)
    if user.org_id:
        q = q.filter(Document.org_id == user.org_id)
    return q.order_by(Document.created_at.desc()).all()


@router.post("/upload", response_model=DocumentOut, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    title: str | None = Form(None),
    site_id: UUID | None = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(Role.TECHNICIAN)),
):
    if not user.org_id:
        raise HTTPException(400, "User has no organization")
    ensure_bucket()
    data = await file.read()
    doc_id = uuid4()
    key = f"org/{user.org_id}/{doc_id}/{file.filename}"
    put_object(key, data, file.content_type or "application/octet-stream")
    doc = Document(
        id=doc_id,
        org_id=user.org_id,
        site_id=site_id,
        title=title or file.filename or "Untitled",
        filename=file.filename or "file",
        content_type=file.content_type or "application/octet-stream",
        storage_key=key,
        size_bytes=len(data),
        status="uploaded",
        created_by=user.id,
        is_demo=False,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    write_audit(
        db,
        action="upload",
        resource_type="document",
        resource_id=str(doc.id),
        user_id=user.id,
        org_id=user.org_id,
        detail={"filename": doc.filename, "size": doc.size_bytes},
    )
    try:
        from app.worker_client import enqueue_document_ingest

        enqueue_document_ingest(str(doc.id))
        doc.status = "processing"
        db.commit()
        db.refresh(doc)
    except Exception:
        _inline_ingest(db, doc, data)
    return doc


def _inline_ingest(db: Session, doc: Document, data: bytes) -> None:
    from app.models import DocumentChunk
    from app.services.rag.search import chunk_text

    try:
        text = data.decode("utf-8", errors="ignore")
    except Exception:
        text = ""
    if not text.strip():
        text = f"[Binary or non-text document: {doc.filename}. Content extraction COMING SOON for PDF/DOCX.]"
    for i, chunk in enumerate(chunk_text(text)):
        db.add(DocumentChunk(document_id=doc.id, chunk_index=i, content=chunk, meta={"source": "inline"}))
    doc.status = "ready"
    db.commit()


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc


@router.get("/{document_id}/content")
def download_document(document_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    data = get_object(doc.storage_key)
    return Response(content=data, media_type=doc.content_type, headers={"Content-Disposition": f'attachment; filename="{doc.filename}"'})
