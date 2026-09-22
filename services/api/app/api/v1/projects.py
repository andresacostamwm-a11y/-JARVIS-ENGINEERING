from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Project, User
from app.schemas.common import ProjectCreate, ProjectOut
from app.api.deps import get_current_user, require_min_role
from app.models.entities import Role
from app.services.audit import write_audit

router = APIRouter()


@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(Project)
    if user.org_id:
        q = q.filter(Project.org_id == user.org_id)
    return q.order_by(Project.created_at.desc()).all()


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(
    body: ProjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(Role.ENGINEER)),
):
    if not user.org_id:
        raise HTTPException(400, "User has no organization")
    proj = Project(**body.model_dump(), org_id=user.org_id, is_demo=False)
    db.add(proj)
    db.commit()
    db.refresh(proj)
    write_audit(
        db,
        action="create",
        resource_type="project",
        resource_id=str(proj.id),
        user_id=user.id,
        org_id=user.org_id,
    )
    return proj


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(404, "Project not found")
    return proj
