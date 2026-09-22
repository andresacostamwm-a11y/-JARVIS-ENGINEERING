from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Asset, User
from app.schemas.common import AssetCreate, AssetUpdate, AssetOut
from app.api.deps import get_current_user, require_min_role
from app.models.entities import Role
from app.services.audit import write_audit

router = APIRouter()


@router.get("", response_model=list[AssetOut])
def list_assets(
    site_id: UUID | None = None,
    q: str | None = None,
    skip: int = 0,
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Asset)
    if site_id:
        query = query.filter(Asset.site_id == site_id)
    if q:
        query = query.filter((Asset.tag.ilike(f"%{q}%")) | (Asset.name.ilike(f"%{q}%")))
    return query.order_by(Asset.tag).offset(skip).limit(limit).all()


@router.post("", response_model=AssetOut, status_code=201)
def create_asset(
    body: AssetCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(Role.TECHNICIAN)),
):
    asset = Asset(**body.model_dump(), is_demo=False)
    db.add(asset)
    db.commit()
    db.refresh(asset)
    write_audit(
        db,
        action="create",
        resource_type="asset",
        resource_id=str(asset.id),
        user_id=user.id,
        org_id=user.org_id,
        detail={"tag": asset.tag},
    )
    return asset


@router.get("/{asset_id}", response_model=AssetOut)
def get_asset(asset_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(404, "Asset not found")
    return asset


@router.patch("/{asset_id}", response_model=AssetOut)
def update_asset(
    asset_id: UUID,
    body: AssetUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(Role.TECHNICIAN)),
):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(404, "Asset not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(asset, k, v)
    db.commit()
    db.refresh(asset)
    write_audit(
        db,
        action="update",
        resource_type="asset",
        resource_id=str(asset.id),
        user_id=user.id,
        org_id=user.org_id,
    )
    return asset


@router.delete("/{asset_id}", status_code=204)
def delete_asset(
    asset_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(Role.ENGINEER)),
):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(404, "Asset not found")
    db.delete(asset)
    db.commit()
    write_audit(
        db,
        action="delete",
        resource_type="asset",
        resource_id=str(asset_id),
        user_id=user.id,
        org_id=user.org_id,
    )
