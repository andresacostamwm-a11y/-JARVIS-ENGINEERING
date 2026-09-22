from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import User
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    TokenError,
)
from app.schemas.common import LoginRequest, RefreshRequest, TokenResponse, UserOut
from app.api.deps import get_current_user
from app.services.audit import write_audit
from jose import JWTError

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email.lower()).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="User inactive")
    access = create_access_token(str(user.id), user.role.value, str(user.org_id) if user.org_id else None)
    refresh = create_refresh_token(str(user.id))
    write_audit(
        db,
        action="login",
        resource_type="user",
        resource_id=str(user.id),
        user_id=user.id,
        org_id=user.org_id,
    )
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = decode_token(body.refresh_token)
        if payload.get("type") != "refresh":
            raise TokenError("not refresh")
    except (JWTError, TokenError):
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    from uuid import UUID

    user = db.query(User).filter(User.id == UUID(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    access = create_access_token(str(user.id), user.role.value, str(user.org_id) if user.org_id else None)
    refresh_tok = create_refresh_token(str(user.id))
    return TokenResponse(access_token=access, refresh_token=refresh_tok)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
