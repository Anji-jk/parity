from datetime import datetime, timedelta, timezone
import secrets
from typing import Optional
from fastapi import status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DBSession

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.firebase import verify_phone_token
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.services.auth.schema import (
    AvailabilityCheckRequest,
    AvailabilityResponse,
    LoginRequest,
    RefreshTokenRequest,
    SignupRequest,
    TokenResponse,
)
from app.shared.db.models.user import AppUser
from app.shared.db.models.user_session import UserSession


def generae_user_id() -> str:
    return f"{secrets.randbelow(10**6):06d}"


class AuthService:
    @staticmethod
    def check_availability(db: DBSession, data: AvailabilityCheckRequest) -> AvailabilityResponse:
        existing_user = db.query(AppUser).filter(
            or_(AppUser.email == data.email, AppUser.phone == data.phone)
        ).first()

        if existing_user:
            if existing_user.email == data.email:
                return AvailabilityResponse(
                    is_available=False,
                    detail="This email is already registered.",
                    conflict_field="email",
                )
            return AvailabilityResponse(
                is_available=False,
                detail="This phone number is already registered.",
                conflict_field="phone",
            )

        return AvailabilityResponse(is_available=True)
    
    @classmethod
    def logout(cls, db: DBSession, data: RefreshTokenRequest) -> None:
        session = (
            db.query(UserSession)
            .filter(UserSession.refresh_token == data.refresh_token)
            .first()
        )
        
        # If the session exists, mark it as revoked to invalidate it
        if session:
            session.is_revoked = True
            db.commit()

    @classmethod
    def register(
        cls, 
        db: DBSession, 
        data: SignupRequest,
        ip_address: Optional[str] = None,
        device_info: Optional[str] = None,
    ) -> TokenResponse:
        # 1. Final duplicate check to prevent race conditions
        availability = cls.check_availability(
            db, AvailabilityCheckRequest(email=data.email, phone=data.phone)
        )
        if not availability.is_available:
            cls._raise_availability_error(availability)

        # 2. Verify Firebase OTP Token against the provided phone
        verify_phone_token(id_token=data.firebase_id_token, expected_phone=data.phone)

        # 3. Create User
        new_user = AppUser(
            id=generae_user_id(),
            firstName=data.firstName,
            lastName=data.lastName,
            email=data.email,
            phone=data.phone,
            isPhoneVerified=True,
            passwordHash=hash_password(data.password),
            userRole=data.role,
        )

        db.add(new_user)
        try:
            db.commit()
            db.refresh(new_user)
        except IntegrityError:
            db.rollback()
            availability = cls.check_availability(
                db, AvailabilityCheckRequest(email=data.email, phone=data.phone)
            )
            if not availability.is_available:
                cls._raise_availability_error(availability)
            raise

        # 4. Log the user in immediately upon successful registration
        return cls._create_or_rotate_session(db, new_user, ip_address, device_info)

    @classmethod
    def login(
        cls,
        db: DBSession,
        data: LoginRequest,
        ip_address: Optional[str] = None,
        device_info: Optional[str] = None,
    ) -> TokenResponse:
        user = None
        if data.email:
            user = db.query(AppUser).filter(AppUser.email == data.email).first()
        elif data.phone:
            user = db.query(AppUser).filter(AppUser.phone == data.phone).first()

        if not user or not user.passwordHash or not verify_password(data.password, user.passwordHash):
            raise AppError(
                "INVALID_CREDENTIALS",
                status.HTTP_401_UNAUTHORIZED,
                "Invalid credentials provided.",
            )

        return cls._create_or_rotate_session(
            db=db,
            user=user,
            ip_address=ip_address,
            device_info=device_info,
        )

    @staticmethod
    def _create_or_rotate_session(
        db: DBSession,
        user: AppUser,
        ip_address: Optional[str] = None,
        device_info: Optional[str] = None,
        existing_session: Optional[UserSession] = None,
    ) -> TokenResponse:
        role_value = (
            user.userRole.value
            if hasattr(user.userRole, "value")
            else str(user.userRole)
        )

        access_token = create_access_token(
            data={"sub": user.id, "role": role_value}
        )
        new_refresh_token = create_refresh_token()
        refresh_expires = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        if existing_session:
            existing_session.refresh_token = new_refresh_token
            existing_session.expires_at = refresh_expires
            if ip_address:
                existing_session.ip_address = ip_address
            if device_info:
                existing_session.device_info = device_info
        else:
            new_session = UserSession(
                id=generae_user_id(),
                user_id=user.id,
                refresh_token=new_refresh_token,
                device_info=device_info,
                ip_address=ip_address,
                is_revoked=False,
                expires_at=refresh_expires,
            )
            db.add(new_session)

        db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            user_id=user.id,
            role=role_value,
        )

    @classmethod
    def rotate_refresh_token(
        cls,
        db: DBSession,
        data: RefreshTokenRequest,
        ip_address: Optional[str] = None,
        device_info: Optional[str] = None,
    ) -> TokenResponse:
        session = (
            db.query(UserSession)
            .filter(UserSession.refresh_token == data.refresh_token)
            .first()
        )

        if not session or session.is_revoked:
            raise AppError(
                "INVALID_REFRESH_TOKEN",
                status.HTTP_401_UNAUTHORIZED,
                "Invalid or revoked refresh token.",
            )

        current_time = datetime.utcnow()
        if session.expires_at < current_time:
            raise AppError(
                "REFRESH_TOKEN_EXPIRED",
                status.HTTP_401_UNAUTHORIZED,
                "Refresh token expired. Please sign in again.",
            )

        user = db.query(AppUser).filter(AppUser.id == session.user_id).first()
        if not user:
            raise AppError(
                "USER_NOT_FOUND",
                status.HTTP_404_NOT_FOUND,
                "Your account could not be found.",
            )

        return cls._create_or_rotate_session(
            db=db,
            user=user,
            ip_address=ip_address,
            device_info=device_info,
            existing_session=session,
        )

    @staticmethod
    def _raise_availability_error(availability: AvailabilityResponse) -> None:
        field = availability.conflict_field
        if field == "email":
            raise AppError(
                "EMAIL_TAKEN",
                status.HTTP_409_CONFLICT,
                availability.detail or "This email is already registered.",
            )
        if field == "phone":
            raise AppError(
                "PHONE_TAKEN",
                status.HTTP_409_CONFLICT,
                availability.detail or "This phone number is already registered.",
            )
        raise AppError(
            "ACCOUNT_CONFLICT",
            status.HTTP_409_CONFLICT,
            "An account with these details is already registered.",
        )
        