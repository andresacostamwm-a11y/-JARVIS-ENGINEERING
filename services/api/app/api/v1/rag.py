from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import User
from app.schemas.common import RagSearchRequest
from app.api.deps import get_current_user
from app.services.rag.search import simple_rag_search

router = APIRouter()


@router.post("/search")
def rag_search(body: RagSearchRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    hits = simple_rag_search(db, body.query, body.limit)
    return {"query": body.query, "hits": hits, "engine": "bag-of-words-mvp"}
