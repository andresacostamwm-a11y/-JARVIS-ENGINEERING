"""FastAPI dependencies: auth + RBAC."""
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.core.security import decode_access_token, TokenError
from app.db.session import get_db
from app.models import User
from app.models.entities import Role

security = HTTPBearer(auto_error=False)

ROLE_RANK = {
    Role.VIEWER: 1,
    Role.AUDITOR: 2,
    Role.TECHNICIAN: 3,
    Role.ENGINEER: 4,
    Role.ENGINEERING_DIRECTOR: 5,
    Role.ADMIN: 6,
}


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if creds is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_access_token(creds.credentials)
    except TokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.id == UUID(payload["sub"])).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive or missing")
    return user


def require_roles(*roles: Role):
    def _inner(user: User = Depends(get_current_user)) -> User:
        if user.role == Role.ADMIN:
            return user
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return user

    return _inner


def require_min_role(min_role: Role):
    def _inner(user: User = Depends(get_current_user)) -> User:
        if ROLE_RANK.get(user.role, 0) < ROLE_RANK[min_role]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return user

    return _inner
