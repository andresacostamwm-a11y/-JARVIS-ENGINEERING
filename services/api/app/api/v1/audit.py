from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import AuditEvent, User
from app.api.deps import get_current_user, require_min_role
from app.models.entities import Role

router = APIRouter()


@router.get("/events")
def list_events(
    skip: int = 0,
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(Role.AUDITOR)),
):
    q = db.query(AuditEvent)
    if user.org_id and user.role != Role.ADMIN:
        q = q.filter(AuditEvent.org_id == user.org_id)
    rows = q.order_by(AuditEvent.created_at.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": str(e.id),
            "action": e.action,
            "resource_type": e.resource_type,
            "resource_id": e.resource_id,
            "user_id": str(e.user_id) if e.user_id else None,
            "detail": e.detail,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in rows
    ]
