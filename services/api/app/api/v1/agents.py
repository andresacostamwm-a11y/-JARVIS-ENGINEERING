from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import User, AgentRun
from app.schemas.common import AgentRunRequest, ChatMessage, ChatRequest
from app.api.deps import get_current_user
from app.api.v1.chat import chat

router = APIRouter()


@router.post("/run")
async def agents_run(
    body: AgentRunRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Alias: run agent with a single prompt (uses chat + tools)."""
    req = ChatRequest(
        messages=[ChatMessage(role="user", content=body.prompt)],
        use_tools=body.use_tools,
        stream=False,
    )
    return await chat(req, db=db, user=user)


@router.get("/runs")
def list_runs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(AgentRun)
    if user.org_id:
        q = q.filter(AgentRun.org_id == user.org_id)
    rows = q.order_by(AgentRun.created_at.desc()).limit(50).all()
    return [
        {
            "id": str(r.id),
            "status": r.status,
            "prompt": r.prompt[:200],
            "provider": r.provider,
            "model": r.model,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
