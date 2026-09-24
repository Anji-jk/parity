from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models import (
    InviteMethod,
    Property,
    PropertyWorkerStatus,
    Role,
    Session as UserSession,
    User,
)
from app.modules.auth.schema import LoginRequest, SignupRequest, TokenResponse


class AuthService:
    @staticmethod
    def register(db: DBSession, data: SignupRequest) -> User:
        # Check if email is already registered
        if db.query(User).filter(User.email == data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists."
            )

        # Determine role: assigned property designates worker, otherwise owner/tenant
        if data.assigned_property_id:
            property_exists = db.query(Property).filter(Property.id == data.assigned_property_id).first()
            if not property_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Assigned property does not exist."
                )
            role = Role.WORKER
            worker_status = PropertyWorkerStatus.ACTIVE
            invited_via = data.invited_via or InviteMethod.CODE
        else:
            role = Role.OWNER
            worker_status = None
            invited_via = None

        new_user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            phone=data.phone,
            password_hash=hash_password(data.password),
            role=role,
            assigned_property_id=data.assigned_property_id,
            worker_status=worker_status,
            invited_via=invited_via,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def login(db: DBSession, credentials: LoginRequest) -> TokenResponse:
        user = db.query(User).filter(User.email == credentials.email).first()
        if not user or not user.password_hash or not verify_password(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        # Generate stateless access token with role claim
        access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
        refresh_token = create_refresh_token()

        # Save session record
        session_entry = UserSession(
            user_id=user.id,
            refresh_token=refresh_token,
            device_info=credentials.device_info,
            ip_address=credentials.ip_address,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        db.add(session_entry)
        db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            role=user.role,
            user_id=user.id,
        )