from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session as DBSession

from src.core.config import settings
from src.core.exceptions import AppError
from src.shared.db.enums.role import Role
from src.shared.db.config.session import get_db
from src.shared.db.models.user import AppUser

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: DBSession = Depends(get_db),
) -> AppUser:
    if credentials is None:
        raise AppError(
            "UNAUTHORIZED",
            status.HTTP_401_UNAUTHORIZED,
            "Please sign in to continue.",
        )

    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise AppError(
                "UNAUTHORIZED",
                status.HTTP_401_UNAUTHORIZED,
                "Your session is invalid. Please sign in again.",
            )
    except JWTError:
        raise AppError(
            "UNAUTHORIZED",
            status.HTTP_401_UNAUTHORIZED,
            "Your session is invalid or expired. Please sign in again.",
        )

    user = db.query(AppUser).filter(AppUser.id == user_id).first()
    if not user:
        raise AppError(
            "UNAUTHORIZED",
            status.HTTP_401_UNAUTHORIZED,
            "Your account could not be found. Please sign in again.",
        )
    return user


def require_owner(current_user: AppUser = Depends(get_current_user)) -> AppUser:
    if current_user.userRole != Role.OWNER:
        raise AppError(
            "FORBIDDEN",
            status.HTTP_403_FORBIDDEN,
            "An owner account is required for this action.",
        )
    return current_user


def require_worker(current_user: AppUser = Depends(get_current_user)) -> AppUser:
    if current_user.userRole != Role.WORKER:
        raise AppError(
            "FORBIDDEN",
            status.HTTP_403_FORBIDDEN,
            "A worker account is required for this action.",
        )
    return current_user